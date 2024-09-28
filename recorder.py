from time import sleep, time
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import KeyCode, Key
import json, threading

class Recorder:
    def __init__(self, ui_window):
        self.ui_window = ui_window
        self.recording = False
        self.playback = False
        self.mouse_listener = None
        self.keyboard_listener = None
        self.events = []
        self.recordtime = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.button_dict = {Button.left:"left_click", Button.right:"right_click", Button.middle:"middle_click", Button.x1:"side1_click", Button.x2:"side2_click"}


    def start_recording(self):
        self.recording = True
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.recordtime = time()

    def stop_recording(self):
        self.recording = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        self.mouse_listener = None
        self.keyboard_listener = None
        self.event_to_json()
        self.events = []

    def event_to_json(self):
        with open('macro.json', 'w') as savefile:
            #print(self.events)
            json.dump(self.events, savefile, indent = 4)

    def on_move(self, x, y):
        self.events.append({"type":"move", "time":time() - self.recordtime, "x":x, "y":y})
        #x, y, time
        #print('Pointer moved to {0}'.format(
        #(x, y)))

    def on_click(self, x, y, button, pressed):
        if button == Button.unknown:
            return
        self.events.append({"type":self.button_dict[button], "time":time() - self.recordtime, "x":x, "y":y, "pressed":pressed})
        #print('{0} at {1}'.format(
        #    'Pressed' if pressed else 'Released',
        #    (x, y)))
        #print(button, pressed)

    def on_scroll(self, x, y, dx, dy):
        self.events.append({"type":"scroll", "time":time() - self.recordtime, "x":x, "y":y, "dx":dx, "dy":dy})

        #print('Scrolled {0} at {1}'.format(
        #    'down' if dy < 0 else 'up',
        #   (x, y)))
        #print(dx,dy)

    def on_press(self, key):
        _key = self.serialize_key(key)
        print(type(_key))
        self.events.append({"type":"key_press", "time":time() - self.recordtime, "key":_key})
        #try:
            #print('alphanumeric key {0} pressed'.format(
                #key.char))
        #except AttributeError:
            #print('special key {0} pressed'.format( 
                #key))

    def on_release(self, key):
        _key = self.serialize_key(key)
        print(type(_key))

        self.events.append({"type":"key_release", "time":time() - self.recordtime, "key":_key})
        #print('{0} released'.format(
            #key))
        #if key == keyboard.Key.esc:
            # Stop listener
            #return False

    def start_playback(self):
        threading.Thread(target=self.playback_thread).start()

    def playback_thread(self):
        self.playback = True
        self.ui_window.record_button_switch(False)
        self.ui_window.playback_button_switch(False)
        
        with open("macro.json", "r") as savefile:
            macro_events = json.load(savefile)

        reverse_button_dict = {value:key for key,value in self.button_dict.items()}
        start_time = time()
        for event in macro_events:

            sleep_time = max(0,event["time"] - (time() - start_time))
            if sleep_time:
                sleep(sleep_time)

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
                print(key)
                self.keyboard_controller.press(key)
            elif event["type"] == "key_release":
                key = self.deserialize_key(event["key"])
                print(type(key))
    
                self.keyboard_controller.release(key)

        self.playback = False
        self.ui_window.record_button_switch(True)
        self.ui_window.playback_button_switch(True)
    def serialize_key(self, key):
        if "Key." in str(key):
            return str(key)
        return key.char

    def deserialize_key(self, key):
        if "Key." in key:
            return eval(key)
        return key

    def is_recording(self):
        return self.recording
    
    def is_playbacking(self):
        return self.playback