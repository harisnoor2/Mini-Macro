from ui import Window
import json

if __name__ == "__main__":
    try:
        settings= open("settings.json", 'r')
    except FileNotFoundError:
        default_settings = {"record":"Ctrl Shift Alt R", "playback":"Ctrl Shift Alt P", "speed":1, "playback_count":1}
        with open("settings.json", 'w') as settings_file:
            json.dump(default_settings, settings_file, indent = 4)
    app = Window()
    app.run()