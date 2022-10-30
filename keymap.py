import logging

import time

from threading import Thread
from types import FunctionType
from typing import Callable, Optional
from configparser import ConfigParser
from outputs import KeyboardOutputs, MouseOutputs, LogOutputs, PrintOutputs
from dataclasses import dataclass, fields
import random

def handle_dev_command(message: str):
    match message:
        case "edit":
            print(f"Edit dev command: {message}")
        case "add":
            print(f"Add dev command: {message}")
        case "move":
            print(f"Mode dev command: {message}")
        case "undo":
            print(f"Undo dev command: {message}")
        case _:
            print(f"Unknown dev command: {message}")

@dataclass
class DevCommand:
    keys: list[str]
    commands: list[str]
    is_dev_command = True
    fn: Callable = handle_dev_command

    def run(self, message: str) -> bool:
        self.fn(message.split(maxsplit=1)[1])
        return True

@dataclass
class Command:
    keys: list[str]
    fn: Callable
    button: str
    duration: Optional[float] = None
    repeats: Optional[int] = None
    cooldown: Optional[float] = None
    random_chance: Optional[int] = None

    enabled: bool = True
    is_dev_command: bool = False

    last_run: float = 0
    is_running: bool = False # TODO this needs to be a mutex

    def __post_init__(self):
        if self.duration and not isinstance(self.duration, float):
            self.duration = float(self.duration)
        if self.repeats and not isinstance(self.repeats, int):
            self.repeats = int(self.repeats)
        if self.cooldown and not isinstance(self.cooldown, float):
            self.cooldown = float(self.cooldown)
        if self.random_chance and not isinstance(self.random_chance, int):
            self.random_chance = int(self.random_chance)

    @staticmethod
    def tags_to_arg_dict() -> dict:
        return {
            "cd": "cooldown",
            "d":  "duration", # from API
            "n":  "repeats", # from API
            "r":  "random_chance"
        }

    @classmethod
    def tag_to_arg(cls, tag: str) -> Optional[str]:
        try:
            return cls.tags_to_arg_dict()[tag]
        except KeyError:
            return None

    def is_on_cooldown(self) -> bool:
        delta = time.time() - self.last_run
        if self.cooldown:
            return delta < self.cooldown
        return False

    def check_random_chance_success(self) -> bool:
        if self.random_chance:
            if 0 == self.random_chance:
                return False
            return random.randint(0,100) <= self.random_chance
        return True

    def can_run(self) -> bool:
        if not self.is_running:
            if not self.is_on_cooldown():
                if self.check_random_chance_success():
                    return True
                else:
                    print(f"{self.keys} failed random chance of {self.random_chance}%")
            else:
                print(f"{self.keys} is on cooldown")
        else:
            print(f"{self.keys} is already running")
        return False

    def get_runner(self) -> Optional[Callable]:
        if self.can_run():
            self.last_run = time.time()

            def fn() -> None:
                self.is_running = True
                self.fn(self.button, self.duration, self.repeats) # TODO kwargs?
                self.is_running = False

            return fn
        return None

    def run(self, message: str = None) -> bool:
        runner = self.get_runner()
        if runner:
            Thread(target=runner).start()
            return True
        return False

def execute_runners(runners: list[Callable]):
    for runner in runners:
        thread = Thread(target=runner)
        thread.start()
        thread.join()
        # TODO this will need to lock the commands for the duration of the whole thing

Keymap = list[Command | DevCommand]

MOUSE_COMMAND_MAP = {
    "lmb": "left",
    "mmb": "middle",
    "rmb": "right",
    "move": "move"
}

MOUSE_IDENTITY_MATRIX = {
    "right":    (1,  0),
    "left":     (-1, 0),
    "up":       (0,  -1),
    "down":     (0,  1),
}

def split_csv(keys: str, delimiter: str = ',') -> list[str]:
    return [s.strip() for s in keys.split(delimiter)]


def make_mouse_keymap(config: ConfigParser, section: str = None, is_dev: bool = False) -> Keymap:
    ret = []

    for k, v in config[section or 'mouse.chat.commands'].items():
        commands, actions = (split_csv(k, ','), split_csv(v, ','))

        actions_splitted = actions[0].split()
        actions[0] = [MOUSE_COMMAND_MAP[actions_splitted[0]]] + actions_splitted[1:]
        button = " ".join(actions[0])
        args = actions[1:]

        kwargs = {}
        for arg in args:
            kwarg_key, kwarg_value = arg.split(':')
            command_key = Command.tag_to_arg(kwarg_key)
            if command_key:
                kwargs[command_key] = float(kwarg_value) # FIXME sanitise this cast

        if is_dev:
            kwargs["is_dev_command"] = True

        ret.append(Command(commands,
                            MouseOutputs.press_release_routine,
                            button,
                            **kwargs)
        )

    return ret

def make_keyboard_keymap(config: ConfigParser, section: str = None, is_dev: bool = False) -> Keymap:
    ret = []

    for k, v in config[section or 'keyboard.chat.commands'].items():
        commands, actions = (split_csv(k, ','), split_csv(v, ','))

        button = actions[0]
        args = actions[1:]
        kwargs = {}
        for arg in args:
            kwarg_key, kwarg_value = arg.split(':')
            command_key = Command.tag_to_arg(kwarg_key)
            if command_key:
                kwargs[command_key] = float(kwarg_value) # FIXME sanitise this cast
        if is_dev:
            kwargs["is_dev_command"] = True

        ret.append(Command(commands,
                            KeyboardOutputs.press_release_routine,
                            button,
                            **kwargs)
        )

    return ret

def make_dev_commmands_keymap(config: ConfigParser, section: str = None, is_dev: bool = False) -> Keymap:
    ret = []

    for k, v in config[section or 'dev.chat.commands'].items():
        commands, subcommands = (split_csv(k, ','), split_csv(v, ','))

        ret.append(DevCommand(commands, subcommands))

    return ret

def make_dev_keymap(config: ConfigParser) -> Keymap:
    dev_keymap = make_dev_commmands_keymap(config, "dev.chat.commands", is_dev = True)
    keyboard_keymap = make_keyboard_keymap(config, "dev.chat.commands.keyboard", is_dev = True)
    mouse_keymap = make_mouse_keymap(config, "dev.chat.commands.mouse", is_dev = True)
    return keyboard_keymap + mouse_keymap + dev_keymap

def make_keymap_entry(config: ConfigParser) -> Keymap:
    return make_keyboard_keymap(config) + make_mouse_keymap(config) + make_dev_keymap(config)

def log_keymap(keymap: Keymap, to_console = False) -> str:
    out_fn = logging.debug if not to_console else print
    public = ""
    dev = ""
    for command in keymap:
        if isinstance(command, Command):
            temp = f"{command.keys} => button={command.button}, duration={command.duration}, cooldown={command.cooldown}sec, repeats={command.repeats}, random_chance={command.random_chance or 100}%, enabled={command.enabled}\n"
            if not command.is_dev_command:
                public = public + temp
            else:
                dev = dev + temp
        elif isinstance(command, DevCommand):
            dev = dev + f"{command.keys} => subcommands={command.commands}\n"
    rep = f"Public Commands:\n{public}\nDev Commands:\n{dev}"
    out_fn(rep)
    return rep

    if to_console:
        out_fn = print

        key_length  = max(len(k) for k in keymap.keys())
        key_padding = 5
        key_space   = key_length + key_padding

        func_length  = max(len(v[0].__qualname__) for v in keymap.values())
        func_padding = 1
        func_space   = func_length + func_padding

        for k, v in keymap.items():
            out_fn(f"{k:{key_space}}: ({v[0].__qualname__:{func_space}}, {v[1]})")
    else:
        for command in keymap:
            out_fn(f"{command.keys} => {command.button=}, {command.duration=}, {command.cooldown=}, {command.repeats=}, {command.random_chance=}%, {command.enabled=}")

easter_eggs: Keymap = {
    "!dungeon": (PrintOutputs.printer, ("In the dungeon, the dark cold dungeon, the mods will start a mutiny tonight! Ahhhhh wooooo!",)),
    "!caulk": (PrintOutputs.printer, ("Caulk or, less frequently, caulking is a material used to seal joints or seams against leakage in various structures and piping.",)),
    "!cock": (PrintOutputs.printer, ("Hahahaha, why did you say cock?",)),
    "!tiethepoll": (PrintOutputs.printer, ("Kat loves it when chat ties the poll!",)),
    "!sosig": (PrintOutputs.printer, ("Kat is a silly sosig!",)),
}