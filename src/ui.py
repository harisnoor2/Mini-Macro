import tkinter as tk
from recorder import Recorder
from tkinter import messagebox, filedialog, Toplevel
import json
from PIL import Image, ImageTk
class Window:
    def __init__(self):

        with open("settings.json", 'r') as  settings_file:
            self.settings = json.load(settings_file)

        self.root = tk.Tk()
        self.root.title("Mini Macro")
        self.root.geometry("265x100")
        self.root.resizable(False,False)
        self.saved_file_path = None
        self.recorder = Recorder(self, self.settings)
        self.rec_img = self.resize_image("src/assets/record.png", (50, 50))
        self.stop_img = self.resize_image("src/assets/stop.png", (50, 50))
        self.play_img = self.resize_image("src/assets/play.png", (50, 50))
        self.record_button = tk.Button(self.root, image=self.rec_img, command = self.start_recording)
        #self.record_button.pack()
        self.playback_button = tk.Button(self.root, image = self.play_img, command = self.start_playback, state="disabled")
        #self.playback_button.pack()
        self.record_button.grid(row=0, column=0, padx=38, pady=(10,10))  # Add padding to the buttons
        self.playback_button.grid(row=0, column=1, padx=38, pady=(10,10))
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        menu_bar.add_cascade(label="File", menu=file_menu)

        hotkey_menu = tk.Menu(menu_bar, tearoff=0)
        hotkey_recording_choice_menu = tk.Menu(hotkey_menu, tearoff=0)
        hotkey_menu.add_cascade(label="Recording", menu=hotkey_recording_choice_menu)

        self.recording_var = tk.StringVar(value=self.settings["record"])

        hotkey_recording_choice_menu.add_radiobutton(label="Ctrl Shift Alt R", variable=self.recording_var, value="Key.ctrl,Key.shift,Key.alt,r", command=self.change_hotkey)
        hotkey_recording_choice_menu.add_radiobutton(label="F8", variable=self.recording_var, value="Key.f8", command=self.change_hotkey)
        hotkey_recording_choice_menu.add_radiobutton(label="F12", variable=self.recording_var, value="Key.f12", command=self.change_hotkey)
        hotkey_recording_choice_menu.add_radiobutton(label="Esc", variable=self.recording_var, value="Key.esc", command=self.change_hotkey)
        hotkey_playback_choice_menu = tk.Menu(hotkey_menu, tearoff=0)

        self.playback_var = tk.StringVar(value=self.settings["playback"])

        hotkey_playback_choice_menu.add_radiobutton(label="Ctrl Shift Alt P", variable=self.playback_var, value="Key.ctrl,Key.shift,Key.alt,p", command=self.change_hotkey)
        hotkey_playback_choice_menu.add_radiobutton(label="F8", variable=self.playback_var, value="Key.f8", command=self.change_hotkey)
        hotkey_playback_choice_menu.add_radiobutton(label="F12", variable=self.playback_var, value="Key.f12", command=self.change_hotkey)
        hotkey_playback_choice_menu.add_radiobutton(label="Esc", variable=self.playback_var, value="Key.esc", command=self.change_hotkey)
        hotkey_menu.add_cascade(label="Playback", menu=hotkey_playback_choice_menu)
        
        menu_bar.add_cascade(label="Hotkeys", menu=hotkey_menu)
        playback_menu = tk.Menu(menu_bar, tearoff=0)
        playback_menu.add_command(label="Amount", command=self.set_playback_amount)
        menu_bar.add_cascade(label="Playback", menu=playback_menu)

        self.root.iconbitmap("src/assets/minimacro.ico")
        self.root.config(menu=menu_bar)

    def resize_image(self, image_path, size):
        image = Image.open(image_path)
        resized_image = image.resize(size)  # Use ANTIALIAS for better quality
        return ImageTk.PhotoImage(resized_image)
    
    def set_playback_amount(self):
        amount_window = Toplevel(self.root)
        amount_window.title("Set Playback Amount")
        amount_window.geometry("200x80")
        tk.Label(amount_window, text="Playback Amount (0-10):\nSet to 0 for inf").pack()
        amount_entry = tk.Entry(amount_window)
        amount_entry.insert(0, self.settings["playback_amount"])
        amount_entry.pack()
        submit_button = tk.Button(amount_window, text="Submit", 
            command=lambda: self.save_playback_amount(amount_entry.get(), amount_window))
        submit_button.pack()

    def save_playback_amount(self, value, window):
        try:
            playback_amount = int(value)
            if playback_amount < 0:
                raise ValueError
            else:
                self.settings["playback_amount"] = playback_amount
                self.update_settings()
                window.destroy()

        except ValueError:
            messagebox.showwarning("WARNING", "Invalid Value")

    def change_hotkey(self):
        if self.recording_var.get() == self.playback_var.get():
            messagebox.showwarning("WARNING", "Hotkey Conflict")
            self.playback_var.set("Key.ctrl,Key.shift,Key.alt,p")
        else:
            self.settings["record"] = self.recording_var.get()
            self.settings["playback"] = self.playback_var.get()
            self.update_settings()

    def update_settings(self):
        with open("settings.json", "w") as settings_file:
            json.dump(self.settings, settings_file, indent = 4)
        self.recorder._update_settings(self.settings)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=(("Text Files", "*.json"), ("All Files", "*.*"))
        )
        print(file_path)
        if file_path:
            if self.recorder.json_to_event(file_path):
                self.playback_button.config(state="active")
                self.saved_file_path = file_path
                self.playback_button_switch(True)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save a File",
            defaultextension=".json",
            filetypes=(("Text Files", "*.json"), ("All Files", "*.*"))
        )
        if file_path:
            self.saved_file_path = file_path
            self.recorder.event_to_json(self.saved_file_path)

    def run(self): 
        self.root.mainloop()
    
    def start_recording(self):
        if self.recorder.is_recording():
            self.record_button.config(image=self.rec_img)
            self.recorder.stop_recording()
            self.playback_button_switch(True)
        else:
            self.saved_file_path = None
            self.record_button.config(image=self.stop_img)
            self.recorder.start_recording()
            self.playback_button_switch(False)


    def record_button_switch(self, enabled):
        if enabled:
            self.record_button.config(state="active")
            self.playback_button.config(image=self.play_img)
        else:
            self.record_button.config(state="disabled")
            self.playback_button.config(image=self.stop_img)


    def playback_button_switch(self, enabled):
        if enabled:
            self.playback_button.config(state="active")
        else:
            self.playback_button.config(state="disabled")

    def start_playback(self):
        if self.recorder.is_loaded():
            if self.recorder.is_playbacking():
                self.recorder.stop_playback()
                self.playback_button.config(image=self.play_img)

            else:
                self.recorder.start_playback()
                self.playback_button.config(image=self.stop_img)