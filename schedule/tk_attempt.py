from tkinter import *
from tkinter import ttk
from Tk.TableEntry import TableEntry

root = Tk()
root.title("TableEntry test (plz don't crash)")
# root.grid()
mainframe = Frame(root)
mainframe.grid()
# mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
table_entry = TableEntry(mainframe,
                         columns=5,
                         rows=4,
                         titles=["lorem", "ipsum", "dolor", "yadda", "whatever"])
table_entry.grid(row=0, column=0)

root.mainloop()
