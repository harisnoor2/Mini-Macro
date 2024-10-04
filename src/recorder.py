from time import sleep, time
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key
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
        self._update_settings(self.settings)
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
        self.modifier_states = {
            'ctrl': False,
            'shift': False,
            'alt': False
        }

    def is_loaded(self):
        return len(self.events)

    def is_recording(self):
        return self.recording
    
    def is_playbacking(self):
        return self.playback

    def _update_settings(self, settings):
        self.settings = settings
        keys = self.settings["record"].split(',')
        if len(keys) == 1:
            self.rec_hotkey = [keys[0], False]
        else:
            self.rec_hotkey = [keys[-1], True]
        keys = self.settings["playback"].split(',')
        if len(keys) == 1:  
            self.play_hotkey = [keys[0], False]
        else:
            self.play_hotkey = [keys[-1], True]

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
        if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r]:
            self.modifier_states['ctrl'] = True
        elif key in [Key.shift, Key.shift_l, Key.shift_r]:
            self.modifier_states['shift'] = True
        elif key in [Key.alt, Key.alt_l, Key.alt_r]:
            self.modifier_states['alt'] = True
        
        _key = self.serialize_key(key)

        if _key == self.rec_hotkey[0]:
            if self.rec_hotkey[1] == True:
                if all(self.modifier_states.values()):
                    self.ui_window.start_recording()
                    return
            else:
                self.ui_window.start_recording()
                return

        if _key == self.play_hotkey[0]:
            if self.play_hotkey[1] == True:
                if all(self.modifier_states.values()):
                    self.ui_window.start_playback()
                    self.recording = False
                    return
            else:
                self.ui_window.start_playback()
                self.recording = False
                return

        if self.is_recording():
            self.events.append({"type":"key_press", "time":time() - self.recordtime, "key":_key})

    def on_release(self, key):

        if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r]:
            self.modifier_states['ctrl'] = False
        elif key in [Key.shift, Key.shift_l, Key.shift_r]:
            self.modifier_states['shift'] = False
        elif key in [Key.alt, Key.alt_l, Key.alt_r]:
            self.modifier_states['alt'] = False

        if self.is_recording():
            _key = self.serialize_key(key)
            self.events.append({"type":"key_release", "time":time() - self.recordtime, "key":_key})

    def unpress_keys(self):
        keys = {}
        for event in self.events:
            if event["type"] == "key_press":
                keys.add(event["key"])
        for key in keys:
            self.keyboard_controller.release(self.deserialize_key(key))
        for mouse_button in self.button_dict.keys():
            self.mouse_controller.release(mouse_button)


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
        playback_amount = self.settings["playback_amount"]
        inf_playback = True

        while inf_playback:
            if playback_amount == 0:
                _playback_amount = 1
            else:
                _playback_amount = playback_amount
                inf_playback = False

            for i in range(_playback_amount):
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
                if not self.is_playbacking():
                    break
            if  not self.is_playbacking():
                break

        self.unpress_keys()
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