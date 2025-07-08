from functools import partial
from tkinter import *
from tkinter.simpledialog import Dialog

class A:
    # creates parent window
    def __init__(self):

        self.popup_menu = None
        self.mw = Tk()
        self.mw.geometry('500x500')

        self.frame = Frame(self.mw)
        self.frame.pack()
        self.label = Label(self.frame,
                                    text = "Hello",)
        self.label.pack()
        self.button = Button(self.frame, text="Show Dialog", command=partial(self.dialog, self.frame, "Testing"),
                             background="yellow")
        self.button.pack()

    def dialog(self,frame, title, *_):
        die = Dialog(frame,title)

    def run(self):
        mainloop()


a = A()
a.run()
