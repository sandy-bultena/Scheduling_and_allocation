from functools import partial
from tkinter import *
from os import path
import sys
sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))


from schedule.Tk.InitGuiFontsAndColours import set_default_fonts_and_colours
from schedule.GUI.DataEntryTk import DataEntryTk, DEColumnDescription


# TODO: button colour changes don't work on mac, not yet tested on windows

def main():
    mw = Tk()
    colours, fonts = set_default_fonts_and_colours(mw, dark_mode=True)
    #print (colours)
    #x = mw.winfo_rgb('systemSelectedTextBackgroundColor')
    #print(x)
    #return
    mw.geometry('400x150')
    mw.title('Button Background Example')
    frame = Frame(mw)
    frame.pack(expand=1, fill=BOTH)

    col_descr = DEColumnDescription("Column 1", 30)
    col2_descr = DEColumnDescription("Column 2", 20)
    col3_descr = DEColumnDescription("Column 3", 15)

    columns = [col_descr,col2_descr, col3_descr]
    data = [[1,2,3],[4,5,6],[7,8,9]]
    data2 = [[21,22,23],[24,25,26],[27,28,29]]

    de = DataEntryTk(frame, columns, data,
                   lambda *args: print("delete",[*args]),
                   lambda *args: print("save", [*args]),
                   bg_colour=colours['DataBackground'],
                   fg_colour=colours['DataForeground'])

    Button(mw, text="clear", command=lambda *_: de.de.clear_data()).pack()
    Button(mw, text="refresh", command=lambda *_: de.refresh(data2)).pack()
    mw.mainloop()


main()