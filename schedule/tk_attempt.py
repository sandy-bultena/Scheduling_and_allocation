from tkinter import *
from tkinter import ttk
from Tk.TableEntry import TableEntry

root = Tk()
root.title("TableEntry test (plz don't crash)")
mainframe = ttk.Frame(root)
table_entry = TableEntry(mainframe, columns=5, rows=4, titles=["lorem", "ipsum"])

root.mainloop()
