from ui import Window

if __name__ == "__main__":
    app = Window()
    app.run()


"""
from pynput import mouse, keyboard
import time, json, threading
from tkinter import *

clientMouse = mouse.Controller()
clientKey = keyboard.Controller()
root = Tk()
#{"inputType" : 0, "location" : (x,y), "time" : 12} # input 1 through 5
root.geometry("265x75")
root.resizable(False,False)
macro = []
recording = False
recordTime = None
#macrojson = open('macro.json', 'w')asdds

def push(inputType, inputTime, inputLocation, inputKeyCode):
    global recordTime
    input = [inputType, inputTime - recordTime, inputLocation, inputKeyCode]
    '''input = {
        "inputType" : inputType, 
        "inputTime" : inputTime,
        "inputLocation" : inputLocation,
        "inputKeyCode" : inputKeyCode
    }'''
    #json.dump(input, macrojson)
    macro.append(input)

def on_press(key):

    threading.Thread(target=push, args=(1, time.time(), None, key)).start()

    #try:
    #    print('alphanumeric key {0} pressed'.format(
    #        key))
    #except AttributeError:
    #    print('special key {0} pressed'.format(
    #        key))

def on_release(key):
    threading.Thread(target=push, args=(2, time.time(), None, key)).start()

    #print('{0} released'.format(
        #key))
    #if key == keyboard.Key.esc:
        # Stop listener
        #return False

def on_move(x, y):
    threading.Thread(target=push, args=(3, time.time(), (x,y), None)).start()

    #print(time.time())

def on_click(x, y, button, pressed):
    print(button, pressed)
    threading.Thread(target=push, args=(4, time.time(), (x,y), (button, pressed))).start()

            
def on_scroll(x, y, dx, dy):
    if dy < 0:
        dy = 2
    threading.Thread(target=push, args=(4+dy, time.time(), (x,y), None)).start()
    #print(dx, dy)
    #print('Scrolled {0} at {1}'.format(
    #    'down' if dy < 0 else 'up',
    #    (x, y)))
    #print(time.time())

mouselistener = None
keyistener = None
def play():
        startTime = time.time()
        for event in macro:
            if (event[1] - (time.time() - startTime)) > 0:
                time.sleep(event[1] - (time.time() - startTime))
            if event[0] == 1:
                clientKey.press(event[3])
            elif event[0] == 2:
                clientKey.release(event[3])
            elif event[0] == 3:
                clientMouse.move(event[2][0] - clientMouse.position[0], event[2][1] - clientMouse.position[1])
            elif event[0] == 4:
                if event[3][1]:
                    clientMouse.press(event[3][0])
                else:
                    clientMouse.release(event[3][0])
            elif event[0] == 5:
                clientMouse.scroll(0,1)
            elif event[0] == 6:
                clientMouse.scroll(0,-1)






def record(self):
    global recording, mouselistener, keylistener, recordTime
    print("ran")
    if recording:
        mouselistener.stop()
        keylistener.stop()
        recording = False
        return
    recordTime = time.time()
    mouselistener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll)
    keylistener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)

    keylistener.start()
    mouselistener.start()
    recording = True


playButton = Button(root, text = "Play", command= play).pack()
recButton = Button(root, text= "Record")
recButton.bind("<ButtonPress-1>", record)
recButton.pack()

root.mainloop()
print(macro)
#macrojson.close()
"""