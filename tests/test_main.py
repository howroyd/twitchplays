import main
import default_config
import keymap

def test_message_filter_basic():
    config = default_config.get_from_file()
    mykeymap = keymap.make_keymap_entry(config)
    
    username = "sussyMcSussFace"
    message  = "forward"
    
    action = main.message_filter((username, message), mykeymap)
    
    assert action