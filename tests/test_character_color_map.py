from scripts.color_utils import generate_color_for_name

def test_generate_color_for_name_format():
    color = generate_color_for_name("TestCharacter999")
    assert isinstance(color, str)
    assert color.startswith("&H")
    assert len(color) == 9  # &H + RRGGBB + &

def test_generate_color_for_name_determinism():
    color1 = generate_color_for_name("ConsistentName")
    color2 = generate_color_for_name("ConsistentName")
    assert color1 == color2

def test_generate_color_for_different_names():
    c1 = generate_color_for_name("NameOne")
    c2 = generate_color_for_name("NameTwo")
    assert c1 != c2
