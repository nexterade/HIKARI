from hikari.ui import IDENTITY, terminal_text


def test_identity_is_exact_unicode():
    assert IDENTITY == "✦"
    assert [f"U+{ord(c):04X}" for c in IDENTITY] == ["U+2726"]


def test_terminal_text_no_longer_forces_identity_on_every_line():
    assert terminal_text("hello") == "hello"
