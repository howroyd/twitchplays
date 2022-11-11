import logging
import random, math

from time import sleep, time_ns
from pynput.keyboard import Controller as Keyboard

from pynput.mouse._win32 import Button
from pynput.mouse._win32 import Controller as Mouse

keyboard = Keyboard()
mouse    = Mouse()

def str_to_button(button: str) -> Button:
    match button:
        case "left":
            return Button.left
        case "middle":
            return Button.middle
        case "right":
            return Button.right
        case _:
            raise KeyError

class KeyboardOutputs:
    @staticmethod
    def press_release_routine(key: str, duration: float, repeats: int) -> None:
        for _ in range(repeats or 1):
            logging.info(f"Press keyboard {key} then wait {duration:.2f}s") # TODO tidy n repeats
            keyboard.press(key)
            sleep(duration / 2)
            keyboard.release(key)
            sleep(duration / 2)

class MouseOutputs:
    @staticmethod
    def press_release_routine(button: str, duration: float = 0.01, repeats: int = 1) -> None:
        button = button.split()
        if 1 == len(button):
            for _ in range(repeats or 1):
                logging.info(f"Press mouse {button[0]} for {duration:.2f}s")
                mouse.press(str_to_button(button[0]))
                sleep(duration or 0.01)
                mouse.release(str_to_button(button[0]))
        else:
            coords = (int(button[1]), int(button[2])) # TODO sanitise cast
            MouseOutputs.move_routine(coords, duration)

    @staticmethod
    def move_routine(coords: tuple[int, int], duration: float = 0.5, randomise: bool = False) -> None:
        duration = duration or 0.5
        x, y = coords
        if x:
            x = random.randint(x//2 - abs(x//2), x + abs(x//2))
        if y:
            y = random.randint(y//2 - abs(x//2), y + abs(y//2))

        print(f"{x=} {y=}")

        steps = max(abs(x/10), abs(y/10))
        timestep = duration / steps

        logging.info(f"Move mouse by x={x}, y={y} in {duration}s ({steps} steps {timestep}s apart)")

        start = time_ns()
        for _ in range(int(steps)):
            mouse.move(int(x / steps), int(y / steps))
            sleep(timestep)
        logging.info(f"Move mouse done in {(time_ns() - start) / 10**9}s ({duration}s)")

    @staticmethod
    def move(x: int, y: int) -> None:
        logging.info(f"Move mouse by x={x}, y={y}")
        mouse.move(x, y)

class LogOutputs:
    @staticmethod
    def log(logstr: str, level: int = logging.INFO) -> None:
        logging.log(level, logstr)

class PrintOutputs:
    @staticmethod
    def printer(*args: str) -> None:
        print(*args)