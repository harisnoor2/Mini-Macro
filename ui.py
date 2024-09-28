import tkinter as tk
from recorder import Recorder

class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mini Macro")
        self.root.geometry("265x75")
        self.root.resizable(False,False)

        self.recorder = Recorder(self)

        self.record_button = tk.Button(self.root, text = "Record", command = self.start_recording)
        #self.record_button.bind("<ButtonPress-1>", self.start_recording)
        self.record_button.pack()
        

        self.playback_button = tk.Button(self.root, text = "Playback", command = self.start_playback)
        self.playback_button.pack()

    def run(self): 
        self.root.mainloop()
    
    def start_recording(self):
        if self.recorder.is_recording():
            self.record_button.config(text="Record")
            self.recorder.stop_recording()
        else:
            self.record_button.config(text="Stop")
            self.recorder.start_recording()

    def record_button_switch(self, enabled):
        if enabled:
            self.record_button.config(state="active")
        else:
            self.record_button.config(state="disabled")

    def playback_button_switch(self, enabled):
        if enabled:
            self.playback_button.config(state="active")
        else:
            self.playback_button.config(state="disabled")

    def start_playback(self):
        self.recorder.start_playback()