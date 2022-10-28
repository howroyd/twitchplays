import logging
import random, math

from time import sleep
#from threading import Thread
#from typing import Union
#
#from pynput.keyboard import Key
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
        for _ in range(repeats):
            logging.info(f"Press keyboard {key} then wait {duration:.2f}s") # TODO tidy n repeats
            keyboard.press(key)
            sleep(duration / 2)
            keyboard.release(key)
            sleep(duration / 2)

    # @staticmethod
    # def press_key_for(key: str, seconds: float = None) -> None:
    #     if seconds:
    #         logging.info(f"Press keyboard {key} for {seconds:.2f}s")
    #         keyboard.press(key)
    #         x = Thread(target=__class__._release_later, args=(key, seconds))
    #         x.start()
    #     else:
    #         logging.info(f"Press keyboard {key}")
    #         keyboard.press(key)
    #         keyboard.release(key)

    # @staticmethod
    # def press_key(key: str) -> None:
    #     __class__.press_key_for(key)

    # @staticmethod
    # def _release_later(key: str, seconds: float = None) -> None:
    #     sleep(seconds)
    #     logging.info(f"Releasing {key}")
    #     keyboard.release(key)

    # @staticmethod
    # def _release(key: str) -> None:
    #     __class__._release_later(key)




class MouseOutputs:
    @staticmethod
    def press_release_routine(button: list[str], duration: float = 0.01, repeats: int = 1) -> None:
        if 1 == len(button):
            for _ in range(repeats):
                logging.info(f"Press mouse {button[0]} for {duration:.2f}s")
                mouse.press(str_to_button(button[0]))
                sleep(duration)
                mouse.release(str_to_button(button[0]))
        else:
            coords = (int(button[1]), int(button[2])) # TODO sanitise cast
            MouseOutputs.move_routine(coords, duration)
            
    @staticmethod
    def move_routine(coords: tuple[int, int], duration: float) -> None:
        x, y = coords
        if x:
            x = random.randint(x//2 - abs(x//2), x + abs(x//2))
        if y:
            y = random.randint(y//2 - abs(x//2), y + abs(y//2))

        print(f"{x=} {y=}")

        steps = max(abs(x/100), abs(y/100))
        timestep = duration / steps
        logging.info(f"Move mouse by x={x}, y={y} in {duration}s ({steps} steps {timestep}s apart)")
        for _ in range(int(steps)):
            mouse.move(int(x / steps), int(y / steps))
            sleep(timestep)

    @staticmethod
    def move(x: int, y: int) -> None:
        logging.info(f"Move mouse by x={x}, y={y}")
        mouse.move(x, y)

    # @staticmethod
    # def _release_later(button: str, seconds: float = None) -> None:
    #     pybutton = str_to_button(button)
    #     sleep(seconds)
    #     logging.info(f"Releasing {button}")
    #     mouse.release(pybutton)

    # @staticmethod
    # def _release(button: str) -> None:
    #     __class__._release_later(button)

class LogOutputs:
    @staticmethod
    def log(logstr: str, level: int = logging.INFO) -> None:
        logging.log(level, logstr)

class PrintOutputs:
    @staticmethod
    def printer(*args: str) -> None:
        print(*args)