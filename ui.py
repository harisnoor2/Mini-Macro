import tkinter as tk
from recorder import Recorder
from tkinter import ttk, messagebox, filedialog
class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mini Macro")
        self.root.geometry("265x75")
        self.root.resizable(False,False)
        self.saved_file_path = None
        self.recorder = Recorder(self)

        self.record_button = tk.Button(self.root, text = "Record", command = self.start_recording)
        self.record_button.pack()

        self.playback_button = tk.Button(self.root, text = "Playback", command = self.start_playback, state="disabled")
        self.playback_button.pack()

        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)

        menu_bar.add_cascade(label="File", menu=file_menu)

        hotkey_menu = tk.Menu(menu_bar, tearoff=0)
        hotkey_menu.add_command(label="Recording", command=self.copy_text)
        hotkey_menu.add_command(label="Playback", command=self.paste_text)

        menu_bar.add_cascade(label="Hotkeys", menu=hotkey_menu)

        playback_menu = tk.Menu(menu_bar, tearoff=0)
        playback_menu.add_command(label="Options", command=self.about_app)

        menu_bar.add_cascade(label="Playback", menu=playback_menu)

        self.root.config(menu=menu_bar)

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

    def copy_text(self):
        messagebox.showinfo("Info", "Text copied!")

    def paste_text(self):
        messagebox.showinfo("Info", "Text pasted!")

    def about_app(self):
        messagebox.showinfo("About", "This is a sample application.")

    def exit_app(self):
        self.root.quit()

    def run(self): 
        self.root.mainloop()
    
    def start_recording(self):
        if self.recorder.is_recording():
            self.record_button.config(text="Record")
            self.recorder.stop_recording()
            self.playback_button_switch(True)
        else:
            self.saved_file_path = None
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