from tkinter import *
from os import path
import sys

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
from schedule.GUI.ColoursTk import get_system_colours, set_system_colours

# TODO: button colour changes don't work on mac

def main():
    mw: Toplevel = Tk()
    colours = get_system_colours(dark=True)
    print(colours)
    mw.configure(background=colours['WorkspaceColour'])
    set_system_colours(mw, colours)
    mw.geometry('400x150')
    mw.title('Button Background Example')

    button = Button(mw, text='Submit', bg='blue', fg='white', activebackground="red")
    button.pack()

    b1 = Button(mw, width=20, text='Button', bg='red')
    b2 = Text(mw, width=40, height=20)
    b2.insert('end', 'hello')

    b1.pack()
    b2.pack()
    # b1.configure({'bg':"#000000"})

    print(f"Button background : {b1.cget('background')}")
    print(f"Button foreground : {b1.cget('foreground')}")

    mw.mainloop()


main()
