import os
from configparser import ConfigParser
import default_config
import pytest

@pytest.fixture
def cfg() -> ConfigParser:
    return default_config.generate_default_config()

def test_keys_in_config(cfg: ConfigParser) -> bool:
    keys = list(default_config.ConfigKeys.as_dict().values())
    assert all(key in cfg for key in keys), "Failed to get keys in config"
    return True

def test_get_from_file() -> None:
    filename = "test_config.ini"
    if os.path.isfile(filename):
        os.remove(filename)
    cfg = default_config.get_from_file(filename)
    ret = test_keys_in_config(cfg)
    os.remove(filename)
    assert not os.path.isfile(filename), "Failed to delete temporary testing file"
    assert ret, "test_get_from_file failed"