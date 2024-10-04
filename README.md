# Mini-Macro

![minimacro](https://github.com/user-attachments/assets/a70999b1-44e5-48e1-ba69-3e5d0ea1652a)

Motivated by TinyTask

Small python application to record and play keyboard and mouse inputs.

Files can be saved and loaded, and are saved as json.
Hotkeys can be edited in the hotkey menu bar, as well as playback amount.

# To build:

Install python and dependencies from requirements.txt, run main.py in src folder

Alternatively you can compile the program into an executable with pyinstaller (also to be installed)

pyinstaller --onefile --windowed --add-data "src/assets;assets" --icon=src/assets/minimacro.ico src/main.py
