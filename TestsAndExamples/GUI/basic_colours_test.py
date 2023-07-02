from tkinter import *
from os import path
import sys

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
from schedule.Tk.InitGuiFontsAndColours import set_default_fonts_and_colours


# TODO: button Colour changes don't work on mac, not yet tested on windows

def main():
    mw: Toplevel = Tk()
    colours = set_default_fonts_and_colours(mw, dark_mode=True)
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
