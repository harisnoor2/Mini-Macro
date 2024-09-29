from time import sleep, time
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import KeyCode, Key
import json, threading


def recording(func):
    def wrapper(self, *args, **kwargs):
        if self.recording:
            return func(self, *args, **kwargs)
    return wrapper

class Recorder:
    def __init__(self, ui_window, settings):
        self.ui_window = ui_window
        self.settings = settings
        self.recording = False
        self.playback = False
        self.current_thread = None
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.mouse_listener.start()
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.keyboard_listener.start()
        self.events = []
        self.recordtime = 0
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.button_dict = {Button.left:"left_click", Button.right:"right_click", Button.middle:"middle_click", Button.x1:"side1_click", Button.x2:"side2_click"}
        self.selected_file = None

    def is_recording(self):
        return self.recording
    
    def is_playbacking(self):
        return self.playback

    def _update_settings(self, settings):
        self.settings = settings

    def start_recording(self):
        self.events = []
        self.recordtime = time()
        self.recording = True

    def stop_recording(self):
        self.recording = False

    def event_to_json(self, save_path = None):
        if save_path:
            with open(save_path, 'w') as save_file:
                json.dump(self.events, save_file, indent=4)

    def json_to_event(self, path):
        with open(path, "r") as load_file:
            try:
                self.events = json.load(load_file)
                return True
            except:
                return False
    @recording
    def on_move(self, x, y):
        self.events.append({"type":"move", "time":time() - self.recordtime, "x":x, "y":y})
    
    @recording
    def on_click(self, x, y, button, pressed):
        if button == Button.unknown:
            return
        self.events.append({"type":self.button_dict[button], "time":time() - self.recordtime, "x":x, "y":y, "pressed":pressed})
   
    @recording
    def on_scroll(self, x, y, dx, dy):
        self.events.append({"type":"scroll", "time":time() - self.recordtime, "x":x, "y":y, "dx":dx, "dy":dy})

    def on_press(self, key):
        rec_hotkey = self.settings["record"]
        play_hotkey = self.settings["playback"]
        _key = self.serialize_key(key)
        if _key == "Key.esc":
            self.ui_window.start_recording()
            return
        if _key == "Key.shift":
            self.ui_window.start_playback()
        self.events.append({"type":"key_press", "time":time() - self.recordtime, "key":_key})

    @recording
    def on_release(self, key):
        _key = self.serialize_key(key)
        self.events.append({"type":"key_release", "time":time() - self.recordtime, "key":_key})
        #if key == keyboard.Key.esc:
            # Stop listener
            #return False

    def stop_playback(self):
        self.playback = False

    def start_playback(self):
        if isinstance(self.current_thread, threading.Thread):
            self.current_thread.join()
        self.current_thread = threading.Thread(target=self.playback_thread)
        self.current_thread.start()

    def playback_thread(self):
        self.playback = True
        self.ui_window.record_button_switch(False)
        macro_events = self.events
        reverse_button_dict = {value:key for key,value in self.button_dict.items()}
        start_time = time()
        for event in macro_events:

            sleep_time = max(0,event["time"] - (time() - start_time))
            if sleep_time:
                sleep(sleep_time)
            if not self.is_playbacking():
                break
            if event["type"] == "move":
                self.mouse_controller.position = (event["x"], event["y"])
            elif "click" in event["type"]:
                self.mouse_controller.position = (event["x"], event["y"])
                if event["pressed"]:
                    self.mouse_controller.press(reverse_button_dict[event["type"]])
                else:
                    self.mouse_controller.release(reverse_button_dict[event["type"]])
            elif event["type"] == "scroll":
                self.mouse_controller.position = (event["x"], event["y"])
                self.mouse_controller.scroll(event["dx"], event["dy"])
            elif event["type"] == "key_press":
                key = self.deserialize_key(event["key"])
                self.keyboard_controller.press(key)
            elif event["type"] == "key_release":
                key = self.deserialize_key(event["key"])
                self.keyboard_controller.release(key)

        self.playback = False
        self.ui_window.record_button_switch(True)
        self.current_thread = None

    def serialize_key(self, key):
        if "Key." in str(key):
            return str(key)
        return self.keyboard_listener.canonical(key).char

    def deserialize_key(self, key):
        if "Key." in key:
            return eval(key)
        return key
