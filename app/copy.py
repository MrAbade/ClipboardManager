from pynput import keyboard
from windows import tag_entry

if __name__ == "__main__":
    COMBINATION = {keyboard.Key.alt, keyboard.Key.ctrl}
    current = set()

    def on_press(key):
        if key in COMBINATION:
            current.add(key)
            if all(k in current for k in COMBINATION):
                tag_entry.tag_entry()

    def on_release(key):
        try:
            current.remove(key)
        except KeyError:
            pass

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
