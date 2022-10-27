import os.path
from configparser import ConfigParser
from dataclasses import dataclass
import pathlib
import shutil

@dataclass(frozen=True, slots=True)
class ConfigKeys:
    logging         = "logging"
    twitch          = "twitch.tv"
    broadcaster     = "broadcaster.commands"
    keyboard        = "keyboard.chat.commands"
    mouse           = "mouse.chat.commands"

    @staticmethod
    def as_dict() -> dict[str, str]:
        objvars = dict(vars(__class__))
        print(objvars)

        keys_to_delete = []

        for k, v in objvars.items():
            if k.startswith("__"):
                keys_to_delete.append(k)
            elif callable(getattr(ConfigKeys(), k)):
                keys_to_delete.append(k)

        for k in keys_to_delete:
            del objvars[k]

        return objvars

def get_from_file(filename: str = "config.ini") -> ConfigParser:
    cfg = ConfigParser()
    if not os.path.isfile(filename):
        print("Config not found, using default and generating a new config file")
        embedded_filename = pathlib.Path(__file__).resolve().parent / "config" / filename
        shutil.copyfile(embedded_filename, filename)
    cfg.read(filename)
    return cfg

def print_config(config: ConfigParser) -> None:
    for key in config[ConfigKeys.default]:
        print(f"""{key} is {config[ConfigKeys.default][key]}""")

    for section in config.sections():
        for key in config[section]:
            print(f"""{key} is {config[section][key]}""")

if __name__ == "__main__":
    cfg = get_from_file("default.ini")
    print_config(cfg)