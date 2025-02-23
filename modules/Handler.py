import wx
import re
import pyautogui
import pygetwindow as gw
import win32gui
import win32con
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
import time
import atexit

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

MOUSE_BUTTONS = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
    "forward": Button.x1,
    "backward": Button.x2
}

patterns = {
    "target": r'target "(.*?)"( multi)?',
    "click": r'mouse click (\w+) at (\d+) (\d+)',
    "move": r'mouse move to (\d+) (\d+)',
    "press": r'keyboard press (\w+)',
    "release": r'keyboard release (\w+)',
    "wait": r'wait (\d+)',
    "type": r'type "(.*?)"',
    "mouse_press": r'mouse press (\w+)',
    "mouse_release": r'mouse release (\w+)',
    "repeat": r'repeat (\d+) times',
    "loop_start": r'loop',
    "loop_end": r'end',
}

def release_all():
    print("\n[Cleaning up resources...]")
    mouseController = MouseController()
    keyboardController = KeyboardController()
    for btn in MOUSE_BUTTONS.values():
        mouseController.release(button=btn)
    for key in keyboard_keys:
        keyboardController.release(key=key)
    print("Done!")

def bring_to_front(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

atexit.register(release_all)

class Handler:
    def __init__(self):
        self.keyboard_keys = keyboard_keys
        self.running = False
        self.pause = False
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    def ParseScript(self, script):
        lines = script.strip().split("\n")
        actions = []
        stack = []
        target_found = False

        for i, line in enumerate(lines):
            line = line.strip()

            if i == 0:
                if not (match := re.match(patterns["target"], line)):
                    wx.MessageDialog(None, "The script must start with a valid 'target' command.", "Error", wx.OK).ShowModal()
                    raise ValueError("ERROR: The script must start with a valid 'target' command.")
                target_found = True
                actions.append({"action": "target", "window": match.group(1), "multi": bool(match.group(2))})
                continue

            if not target_found:
                raise ValueError("ERROR: The script must start with a 'target' command.")

            if match := re.match(patterns["click"], line):
                action = {"action": "click", "button": match.group(1), "x": int(match.group(2)), "y": int(match.group(3))}
                (stack[-1]["actions"] if stack else actions).append(action)

            elif match := re.match(patterns["move"], line):
                action = {"action": "move", "x": int(match.group(1)), "y": int(match.group(2))}
                (stack[-1]["actions"] if stack else actions).append(action)

            elif match := re.match(patterns["press"], line):
                action = {"action": "press", "key": match.group(1)}
                (stack[-1]["actions"] if stack else actions).append(action)

            elif match := re.match(patterns["release"], line):
                action = {"action": "release", "key": match.group(1)}
                (stack[-1]["actions"] if stack else actions).append(action)

            elif match := re.match(patterns["wait"], line):
                action = {"action": "wait", "duration": int(match.group(1))}
                (stack[-1]["actions"] if stack else actions).append(action)

            elif match := re.match(patterns["type"], line):
                action = {"action": "type", "text": match.group(1)}
                (stack[-1]["actions"] if stack else actions).append(action)

            elif match := re.match(patterns["mouse_press"], line):
                action = {"action": "mouse_press", "button": match.group(1)}
                (stack[-1]["actions"] if stack else actions).append(action)

            elif match := re.match(patterns["mouse_release"], line):
                action = {"action": "mouse_release", "button": match.group(1)}
                (stack[-1]["actions"] if stack else actions).append(action)

            elif match := re.match(patterns["repeat"], line):
                repeat_block = {"action": "repeat", "times": int(match.group(1)), "actions": []}
                stack.append(repeat_block)

            elif re.match(patterns["loop_start"], line):
                loop_block = {"action": "loop", "actions": []}
                stack.append(loop_block)

            elif re.match(patterns["loop_end"], line):
                if stack:
                    completed_block = stack.pop()
                    (stack[-1]["actions"] if stack else actions).append(completed_block)
        return actions

    def StopScript(self):
        if not self.running:
            return
        print("Stop Script")
        self.running = False
        release_all()

    def PauseScript(self):
        if not self.running:
            return
        if self.pause:
            print("Resumed Script")
            self.pause = False
        else:
            print("Paused Script")
            self.pause = True

    def RunScript(self, actions, currentWindow=None, isMulti=False):
        windows = None
        win = currentWindow
        multi = isMulti

        for action in actions:
            if action["action"] == "click" and self.running and not self.pause:
                print(f"Click {action['button']} at ({action['x']}, {action['y']})")
                if win:
                    pyautogui.click(win.left + action['x'], win.top + action['y'], button=action['button'])
                else:
                    pyautogui.click(action['x'], action['y'], button=action['button'])

            elif action["action"] == "wait" and self.running and not self.pause:
                print(f"Wait {action['duration']}ms")
                time.sleep(action['duration'] / 1000.0)

            elif action["action"] == "type" and self.running and not self.pause:
                print(f"Type: {action['text']}")
                self.keyboard.type(action['text'])

            elif action["action"] == "press" and self.running and not self.pause:
                print(f"Press: {action['key']}")
                self.keyboard.press(action['key'])

            elif action["action"] == "hold" and self.running and not self.pause:
                print(f"Hold: {action['key']}")
                self.keyboard.press(action['key'])

            elif action["action"] == "release" and self.running and not self.pause:
                print(f"Release: {action['key']}")
                self.keyboard.release(action['key'])

            elif action["action"] == "mouse_press" and self.running and not self.pause:
                print(f"Mouse press: {action['button']}")
                btn = MOUSE_BUTTONS.get(action['button'].lower(), None)
                self.mouse.press(btn)

            elif action["action"] == "mouse_release" and self.running and not self.pause:
                print(f"Mouse hold: {action['button']}")
                btn = MOUSE_BUTTONS.get(action['button'].lower(), None)
                self.mouse.release(btn)

            elif action["action"] == "target":
                print(f"Target: {action['window']} with multi: {action['multi']}")
                multi = action['multi']
                windows = [win for win in gw.getWindowsWithTitle(action['window']) if win.title == action['window']]
                if not windows:
                    wx.MessageDialog(None, "The 'target' window is not found.", "Error", wx.OK).ShowModal()
                    raise ValueError("ERROR: The 'target' window is not found.")
                win = windows[0]
                bring_to_front(win._hWnd)

            elif action["action"] == "loop":
                print("Starting loop...")
                while self.running:
                    while self.pause:
                        if not self.running:
                            return
                        pass
                    if multi:
                        for window in windows:
                            win = window
                            bring_to_front(win._hWnd)
                            self.RunScript(action["actions"], win, multi)
                    else:
                        self.RunScript(action["actions"], win, multi)

            elif action["action"] == "repeat":
                for _ in range(action["times"]):
                    self.RunScript(action["actions"], win, multi)
