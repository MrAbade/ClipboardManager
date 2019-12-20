from pynput import keyboard
from windows import rescue_text

if __name__ == "__main__":
    COMBINATION = {keyboard.Key.ctrl, keyboard.Key.esc}
    current = set()

    def on_press(key):
        if key in COMBINATION:
            current.add(key)
            if all(k in current for k in COMBINATION):
                rescue_text.rescue_text()

    def on_release(key):
        try:
            current.remove(key)
        except KeyError:
            pass

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
