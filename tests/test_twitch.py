import logging
import time
import twitch
import pytest

def channel_connection(channel: str):
    with twitch.ChannelConnection(channel) as tw:
        pass

def channel_connection_with_retries(channel: str) -> bool:
    n_retries = 4
    ret = False

    for i in range(n_retries):
        try:
            channel_connection(channel)
            ret = True
            break
        except (TimeoutError, ConnectionError) as e:
            time.sleep(1)

    return ret

def test_channel_connection(n_retries: int = 4) -> None:
    assert channel_connection_with_retries("katatouille93"), "test_channel_connection failed"

    with pytest.raises(TimeoutError):
        channel_connection("")

def test_message_builder() -> bool:
    test_data = b"Hello"
    x = twitch.MessageBuilderDefault()
    x.append(test_data)
    assert x.buffer == test_data, "Message Builder append buffer failed"
    y = x.get_and_clear()
    assert y == test_data, "Message Builder get buffer failed"
    assert 0 ==len(x.buffer), "Message Builder clear buffer failed"