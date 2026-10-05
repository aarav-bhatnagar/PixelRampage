import tkinter as tk
from tkinter import ttk
from tkinter import *
#Importing all libraries

root = tk.Tk()
root.geometry("500x800")    #Defining the size of the window
root.resizable(0, 0)    #Setting the window to remain at this fixed geometry
root.title("Pixel Art Creator")

#Size of canvas
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400

#Number of pixels on the canvas
XPixels = 16
YPixels = 16

#The fixed width and height of each of these pixels. (16 x 25 = 400)
WIDTH = 25
HEIGHT = 25

#Creates an empty version of the final arraya to be exported
Array = [([0] * XPixels) for _ in range(YPixels)]          #16x16 is the default size

Background = False

Eraser = tk.StringVar(value="False") #Initial value False

def CreateCanvas():
    global canvas
    
    canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")  #Creates the canvas with the set widthxheight
    canvas.pack(anchor=tk.CENTER, expand=True)

    # Re-bind events here
    canvas.bind("<Button-1>", draw) #Binds the left mouse button
    canvas.bind("<B1-Motion>", draw) #Bind the motion of the cursor

def draw(event):
    global Background
    global Array
    XCursorPos, YCursorPos = event.x, event.y   #Gets cursor position on canvas
    #Identifies which pixel and the location of it on the canvas
    Xpos = (XCursorPos // WIDTH) * WIDTH
    Ypos = (YCursorPos // HEIGHT) * HEIGHT
    if 0 <= Xpos <= CANVAS_WIDTH and 0 <= Ypos <= CANVAS_HEIGHT and 0 <= Xpos + WIDTH <= CANVAS_WIDTH and 0 <= Ypos + HEIGHT <= CANVAS_HEIGHT:  #Check against bounds of canvas
        if Eraser.get() == "False":
            canvas.create_rectangle((Xpos, Ypos), (Xpos + WIDTH, Ypos + HEIGHT), fill="black", outline = "") #Draws rectangle as pixel in position
            Array[YCursorPos // HEIGHT][XCursorPos // WIDTH] = 1    #Updates the array
        else:
            #ERASER
            if Array[YCursorPos // HEIGHT][XCursorPos // WIDTH] == 1:   #If the pixel is black
                canvas.create_rectangle((Xpos, Ypos), (Xpos + WIDTH, Ypos + HEIGHT), fill="white", outline = "") #Draw white rectangle
                Array[YCursorPos // HEIGHT][XCursorPos // WIDTH] = 0        #Updates the array
                Background = not Background
                BackgroundChanged() #Re-call background to account for adjustment, i.e. the erased square may be grey or white on checkerboard


def ExportPixels():
    print("Exporting Pixels")
    print(Array)    #Outputs array

# BUTTON FUNCTIONS
def BackgroundChanged(clear=False):
    global Background
    Background = not Background # the new background should be the opposite of the current background setting
    Grey1 = False
    Grey2 = False
    for y in range(YPixels):
        Grey1 = not Grey2   # Top left hand pixel will be grey
        Grey2 = not Grey2 # Alternate Grey2 by the column so that each row starts grey...white...grey etc
        for x in range(XPixels):
            if Grey1:
                if Background:
                    colour = "#E8E9E8"  #grey
                else:
                    colour = "white"    #white
                if Array[y][x] == 0 or clear:
                    canvas.create_rectangle((x*WIDTH, y*HEIGHT), ((x*WIDTH) + WIDTH, (y*HEIGHT) + HEIGHT), fill=colour, outline="")
            Grey1 = not Grey1 # Alternates Grey1 by each square

def ResizeCanvas():
    #Global variable needed to create new canvas
    global Array
    global canvas
    global XPixels
    global YPixels
    global CANVAS_WIDTH
    global CANVAS_HEIGHT
    ClearCanvas()
    print("Resizing Canvas")
    
    canvas.destroy() #Destroyes current canvas
    XPixels = int(canvasWidthEntry.get())
    YPixels = int(canvasHeightEntry.get())
    
    #New canvas width and hight
    CANVAS_WIDTH = XPixels * WIDTH
    CANVAS_HEIGHT = YPixels * HEIGHT
    
    CreateCanvas()
    Array = [([0] * XPixels) for _ in range(YPixels)] #New empty array

    
def ClearCanvas():
    global Array
    global Background
    canvas.delete("all") #Deletes all rectangles on the canvas
    print("Clearing Canvas")
    Array = [([0] * XPixels) for _ in range(YPixels)] #New empty array
    Background = not Background #Re-call background to account for adjustment
    BackgroundChanged(True)
    
title = tk.Label(root, text="Pixel Art Creator")
title.pack()

#Checkboxes - Background and Eraser
ttk.Checkbutton(root,
                text='Background',
                command=BackgroundChanged).pack()

ttk.Checkbutton(root,
                text='Eraser',
                variable=Eraser,
                onvalue='True',
                offvalue='False').pack()


frame = tk.Frame(root)
frame.pack()

canvasWidth = tk.StringVar() #Use of string var to get entry data
canvasHeight = tk.StringVar()

canvasWidthLabel = tk.Label(frame, text="Canvas Width:")
canvasWidthEntry = tk.Entry(frame)

canvasHeightLabel = tk.Label(frame, text="Canvas Height:")
canvasHeightEntry = tk.Entry(frame)

#Labels and input fields arranged in grid format
canvasWidthLabel.grid(row=0, column=0, padx=5, pady=5)
canvasWidthEntry.grid(row=0, column=1, padx=5, pady=5)
canvasHeightLabel.grid(row=1, column=0, padx=5, pady=5)
canvasHeightEntry.grid(row=1, column=1, padx=5, pady=5)

#3 Buttons mapped to function
resizeCanvasButton = tk.Button(root, text="Resize Canvas", command=ResizeCanvas)
resizeCanvasButton.pack(pady=5)

clearCanvasButton = tk.Button(root, text="Clear Canvas", command=ClearCanvas)
clearCanvasButton.pack(pady=5)

exportPixelsButton = tk.Button(root, text="Export Pixels", command=ExportPixels)
exportPixelsButton.pack(pady=5)

CreateCanvas() #Canvas is at the bottom

root.mainloop()