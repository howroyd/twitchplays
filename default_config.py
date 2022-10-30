import os.path
from configparser import ConfigParser
from dataclasses import dataclass
import pathlib
import shutil
import keymap

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

def from_keymap_command(command: keymap.Command) -> str:
    ret = ", ".join(command.keys)
    ret = ret + " = "
    ret = ret + command.button
    if command.duration:
        ret = ret + ", " + \
            list(command.tags_to_arg_dict().keys())[list(command.tags_to_arg_dict().values()).index("duration")] + \
            ':' + str(command.duration)
    if command.repeats:
        ret = ret + ", " + \
            list(command.tags_to_arg_dict().keys())[list(command.tags_to_arg_dict().values()).index("repeats")] + \
            ':' + str(command.repeats)
    if command.cooldown:
        ret = ret + ", " + \
            list(command.tags_to_arg_dict().keys())[list(command.tags_to_arg_dict().values()).index("cooldown")] + \
            ':' + str(command.cooldown)
    if command.random_chance:
        ret = ret + ", " + \
            list(command.tags_to_arg_dict().keys())[list(command.tags_to_arg_dict().values()).index("random_chance")] + \
            ':' + str(command.random_chance)
    return ret


def get_from_file(filename: str = "config.ini") -> ConfigParser:
    cfg = ConfigParser()
    if not os.path.isfile(filename):
        print("Config not found, using default and generating a new config file")
        embedded_filename = pathlib.Path(__file__).resolve().parent / "config" / filename
        shutil.copyfile(embedded_filename, filename)
    cfg.read(filename)
    return cfg

def edit_line(key_to_edit: str, new_data: str, filename: str = "config.ini"):
    cfg = get_from_file(filename)
    for tag in cfg:
        for line in cfg[tag]:
            
            line_split = line.split('=')
            k, v = keymap.split_csv(line_split[0]), keymap.split_csv(line_split[1])
            if key_to_edit in k:
                new_data = keymap.split_csv(new_data)
                if not ':' in new_data[0]:
                    v[0] = new_data[0]
                    new_data = new_data[1:]
                for x in new_data:
                    new_kv = x.split(':')
                    added = False
                    for y in v:
                        if new_kv == y.split(':'):
                            added = True
                            y = x
                            break
                    if not added:
                        v.append(x)
                return
    return

def print_config(config: ConfigParser) -> None:
    for key in config[ConfigKeys.default]:
        print(f"""{key} is {config[ConfigKeys.default][key]}""")

    for section in config.sections():
        for key in config[section]:
            print(f"""{key} is {config[section][key]}""")

if __name__ == "__main__":
    cfg = get_from_file("default.ini")
    print_config(cfg)