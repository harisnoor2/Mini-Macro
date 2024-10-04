from pynput import mouse, keyboard
from pynput.mouse import Button

button_dict = {Button.left:"left_click", Button.right:"right_click", Button.middle:"middle_click", Button.x1:"side1_click", Button.x2:"side2_click"}

print(button_dict.keys())