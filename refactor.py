import time
from dataclasses import dataclass
from typing import Protocol, Callable
from enum import Enum, auto
import functools
import multiprocessing, threading, sys, toml, pprint

OutputFn = Callable[..., threading.Thread | None]

class Permission(Enum):
    DEFAULT = 0
    DEV = 1
    NONE = 2

class Target(Enum):
    NULL = auto()
    LOG = auto()
    KEYBOARD = auto()
    MOUSE = auto()
    DUAL = auto()

@dataclass(slots=True)
class OutputWrapper:
    fn: OutputFn
    target: Target
    permission: Permission = Permission.DEFAULT
    lock: multiprocessing.Lock = None
    name: str = None
    asThread: bool = False

    def __call__(self, *, userPermission: Permission = None, asThread: bool = None) -> threading.Thread | None:
        if not self.fn:
            print(f"Nothing to call for command {self.name}", file=sys.stderr)
            return None
        if self.permission.value > (userPermission or Permission.DEFAULT).value:
            print(f"Insufficient permissions for command {self.name}")
            return None
        if self.lock:
            print(f"{self.name} has a lock but it isnt implemented", file=sys.stderr)
        if (asThread is not None and not asThread) or not self.asThread:
            self.fn()
            return None
        t = threading.Thread(target=self.fn)
        t.start()
        return t

@dataclass(slots=True)
class Command:
    chat: str | list[str]
    output: OutputWrapper
    cooldownSec: float
    randomChance: int

def combine_commands(*outputs: OutputWrapper, waitToComplete: bool = False) -> OutputFn:

    def ret(things: OutputWrapper) -> list[threading.Thread] | None:
        threads = [thing() for thing in things]
        if waitToComplete:
            [thread.join() for thread in threads if thread]
            return None
        return [thread for thread in threads if thread]

    return functools.partial(ret, outputs)

class KeyboardCommands:
    FORWARD = OutputWrapper(
        functools.partial(print, "w"),
        target=Target.KEYBOARD,
        permission=Permission.DEFAULT,
        name="Forward"
    )
    LEFT = OutputWrapper(
        functools.partial(print, "a"),
        target=Target.KEYBOARD,
        permission=Permission.DEFAULT,
        name="Left"
    )

class MouseCommands:
    LOOKRIGHT = OutputWrapper(
        functools.partial(print, "look right"),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="LookRight"
    )
    LOOKLEFT = OutputWrapper(
        functools.partial(print, "look left"),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="LookLeft"
    )
    LMBPRESS = OutputWrapper(
        functools.partial(print, "+lmb"),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="Lmb+"
    )
    LMBRELEASE = OutputWrapper(
        functools.partial(print, "-lmb"),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="Lmb-"
    )

class ComplexCommands:
    RIGHTANDFORWARDCONCURRENT = OutputWrapper(
        combine_commands(
            functools.partial(MouseCommands.LOOKRIGHT, asThread=True),
            functools.partial(KeyboardCommands.FORWARD, asThread=True),
            waitToComplete=True
        ),
        target=Target.DUAL,
        permission=Permission.DEFAULT,
        name="RightAndForwardConcurrent"
    )

    OPENDOOR = OutputWrapper(
        combine_commands(
            MouseCommands.LMBPRESS,
            RIGHTANDFORWARDCONCURRENT,
            MouseCommands.LMBRELEASE,
            MouseCommands.LOOKLEFT
        ),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="OpenDoor"
    )

def keyboard_press(key: str):
    print(f"Pressing keyboard {key}")
def keyboard_release(key: str):
    print(f"Releasing keyboard {key}")
def keyboard_pressrelease(key: str, duration: float = None):
    keyboard_press(key)
    time.sleep(duration or 0.0)
    keyboard_release(key)

def mouse_press(button: str):
    print(f"Pressing mouse {button}")
def mouse_release(button: str):
    print(f"Releasing mouse {button}")
def mouse_pressrelease(button: str, duration: float = None):
    mouse_press(button)
    time.sleep(duration or 0.0)
    mouse_release(button)

def mouse_move(x: int, y: int):
    print(f"Moving mouse {(x,y)}")

def parse_config_keyboard(key: str, value: dict) -> dict[str, Command]:
    if not 'keyboard' == value['device']:
        raise ValueError
    return {
        key:
        Command(
            value.get('chat', None),
            OutputWrapper(
                functools.partial(keyboard_pressrelease, key=value['key'], duration=value.get('duration', 0.0)),
                Target.KEYBOARD,
                name=key
            ),
            value.get('cooldown', None),
            value.get('random', None)
        )
    }

def parse_config_mouse(key: str, value: dict) -> dict[str, Command]:
    if not 'mouse' == value['device']:
        raise ValueError
    if 'button' in value:
        return {
            key:
            Command(
                value.get('chat', None),
                OutputWrapper(
                    functools.partial(mouse_pressrelease, button=value['button'], duration=value.get('duration', 0.0)),
                    Target.MOUSE,
                    name=key
                ),
                value.get('cooldown', None),
                value.get('random', None)
            )
        }
    elif 'move' in value:
        return {
            key:
            Command(
                value.get('chat', None),
                OutputWrapper(
                    functools.partial(mouse_move, value['move'][0], value['move'][1]),
                    Target.MOUSE,
                    name=key
                ),
                value.get('cooldown', None),
                value.get('random', None)
            )
        }
    else:
        raise ValueError

def parse_config_using(key: str, value: dict, existing: dict[str, Command]) -> dict[str, Command]:
    if not 'using' in value:
        raise ValueError
    ret = Command(
        value.get('chat', None),
        None, # TODO
        value.get('cooldown', None),
        value.get('random', None)
    )

    elems = []
    for command in value['using']:
        elems.append(existing[command])

    ret.output = combine_commands(*elems)

    return { key: ret }

def parse_config(fn: str) -> dict[str, Command]:
    ret = {}

    config = toml.load("mytoml.toml")

    for k,v in config['command'].items():
        if 'device' in v:
            if 'keyboard' == v['device']:
                ret |= parse_config_keyboard(k, v)
            elif 'mouse' == v['device']:
                ret |= parse_config_mouse(k, v)
            else:
                raise ValueError
        elif 'using' in v:
            pass
        else:
            raise ValueError

    for k,v in config['command'].items():
        if 'device' in v:
            pass
        elif 'using' in v:
            ret |= parse_config_using(k, v, ret)
        else:
            raise ValueError # TODO superfluous????

    return ret

x = parse_config("mytoml.toml")
print(x)




















threads = [
    threading.Thread(target=ComplexCommands.OPENDOOR, kwargs={"userPermission": Permission.DEV}, name=ComplexCommands.OPENDOOR.name),
]

[t.start() for t in threads]
[t.join() for t in threads]