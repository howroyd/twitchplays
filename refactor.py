from time import sleep
from dataclasses import dataclass
from typing import Protocol, Callable
from enum import Enum, auto
import functools
import multiprocessing, threading, sys, copy

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
class CommandWrapper:
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

def concatenate_callables(*commands, waitToComplete=False) -> OutputFn:
    def ret(things):
        threads = [thing() for thing in things]
        if waitToComplete:
            print("Waiting for threads to complete")
            [thread.join() for thread in threads if thread]
            print("Threads complete")
    return functools.partial(ret, commands)

class KeyboardCommands:
    FORWARD = CommandWrapper(
        functools.partial(print, "w"),
        target=Target.KEYBOARD,
        permission=Permission.DEFAULT,
        name="Forward"
    )
    LEFT = CommandWrapper(
        functools.partial(print, "a"),
        target=Target.KEYBOARD,
        permission=Permission.DEFAULT,
        name="Left"
    )

class MouseCommands:
    LOOKRIGHT = CommandWrapper(
        functools.partial(print, "look right"),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="LookRight"
    )
    LOOKLEFT = CommandWrapper(
        functools.partial(print, "look left"),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="LookLeft"
    )
    LMBPRESS = CommandWrapper(
        functools.partial(print, "+lmb"),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="Lmb+"
    )
    LMBRELEASE = CommandWrapper(
        functools.partial(print, "-lmb"),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="Lmb-"
    )

class ComplexCommands:
    RIGHTANDFORWARDCONCURRENT = CommandWrapper(
        concatenate_callables(
            functools.partial(MouseCommands.LOOKRIGHT, asThread=True),
            functools.partial(KeyboardCommands.FORWARD, asThread=True),
            waitToComplete=True
        ),
        target=Target.DUAL,
        permission=Permission.DEFAULT,
        name="RightAndForwardConcurrent"
    )

    OPENDOOR = CommandWrapper(
        concatenate_callables(
            MouseCommands.LMBPRESS,
            RIGHTANDFORWARDCONCURRENT,
            MouseCommands.LMBRELEASE,
            MouseCommands.LOOKLEFT
        ),
        target=Target.MOUSE,
        permission=Permission.DEFAULT,
        name="OpenDoor"
    )

threads = [
    threading.Thread(target=ComplexCommands.OPENDOOR, kwargs={"userPermission": Permission.DEV}, name=ComplexCommands.OPENDOOR.name),
]

[t.start() for t in threads]
[t.join() for t in threads]