mouse_keys = ["left", "right", "scroll", "scroll-up", "scroll-down", "forward", "backward"]
keyboard_keys = [
    # Modifier keys
    "shift",
    "ctrl",
    "alt",
    "meta",  # Windows key / Command key (Mac)

    # Function keys
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",

    # Navigation keys
    "arrow-up", "arrow-down", "arrow-left", "arrow-right",

    # Editing keys
    "backspace",
    "delete",
    "insert",

    # Enter & Escape
    "enter",
    "escape",

    # Tab & Caps Lock
    "tab",
    "capslock",

    # Page Navigation
    "pageup", "pagedown",
    "home", "end",

    # Numeric keypad
    "numpad-0", "numpad-1", "numpad-2", "numpad-3", "numpad-4",
    "numpad-5", "numpad-6", "numpad-7", "numpad-8", "numpad-9",
    "numpad-decimal", "numpad-add", "numpad-subtract",
    "numpad-multiply", "numpad-divide", "numpad-enter",

    # Letters
    *[chr(k) for k in range(ord('a'), ord('z') + 1)],

    # Numbers
    *[str(k) for k in range(0, 10)],

    # Special characters
    "space",
    "semicolon", "apostrophe", "comma", "period", "slash", "backslash",
    "bracket-left", "bracket-right", "minus", "equal"
]
actions = ["press", "release", "hold", "click"]
events = ["loop", "wait", "repeat"]

class Handler:
    def __init__(self):
        self.mouse_keys = mouse_keys
        self.keyboard_keys = keyboard_keys
        self.actions = actions
        self.events = events

    def Parse(self, text):
        lines = text.splitlines()
        for line in lines:
            word = line.split()
            if word:
                print(word)
