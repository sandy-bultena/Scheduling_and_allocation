from tkinter import *
from tkinter import ttk
from os import path
import sys
import re
from functools import partial
class Foo:
    def __init__(self, cb:callable):
        self.cb = cb
    def run(self):
        self.cb("abc")

def whatever(*args):
    print(*args)

foo = Foo(whatever)
foo.run()
exit()

def get_parents(tree, tree_item_id: str) -> list[object]:
    return list(__get_parent(tree, tree.parent(tree_item_id)))


def __get_parent(tree, tree_item_id: str):
    while tree_item_id != "":
        yield tree_item_id
        tree_item_id = tree.parent(tree_item_id)


sys.path.append(path.dirname(path.dirname(__file__)))
from scrolled import Scrolled

print(path.dirname(path.dirname(__file__)))

# make a Tk window
mw = Tk()
mw.geometry("500x300")

frame = Frame(mw)
frame.pack(expand=1, fill="both")
stv = Scrolled(frame, "Treeview")
stv.pack()
tv = stv.widget

x = tv.insert("", 'end', text="abc")
y = tv.insert(x, 'end', text="a")
z = tv.insert(x, 'end', text='b')
tv.insert(y, 'end', text="hello")
tv.insert(y, 'end', text="salut")
tv.insert(y, 'end', text='bonjour')
tv.insert(z, 'end', text="hello")
tv.insert(z, 'end', text="salut")
tv.insert(z, 'end', text='bonjour')
button = Button(frame, text="Push me", command=lambda: tv.item(y, open=True))
button.pack(expand=1, fill='y')


def selectItem(e, *args):
    print("by mouse position", tv.identify_row(e.y))
    c = tv.identify_row(e.y)

    v = tv.item(c)
    print("getting selection")
    x = tv.selection()
    print(f"{x=}")
    print(f"Focused: {tv.item(x)}")
    button.configure(text=v['text'])


for i in range(25):
    tv.insert(z, 'end', text=i)
tv.item("", open=True)
tv.bind("<Button-2>", selectItem)
print(tv.item(z))
print(x)
print(tv.item(x))
print(tv.item(y))
xr = re.match(r"^=?(\d+)x(\d+)?([+-]\d+[+-]\d+)?$", frame.winfo_toplevel().geometry()).groups()

print(xr)
print(f"parents = {get_parents(tv, z)}")


def open_children(parent):
    tv.item(parent, open=True)
    for child in tv.get_children(parent):
        open_children(child)


def handleOpenEvent(event):
    print("\nOpen event")
    print(event)
    print(tv.focus())


tv.bind('<<TreeviewOpen>>', handleOpenEvent)
print(f"id of x {x}")
print(f"info of abc: {tv.item(x)}")
print(f"parent of x '{tv.parent(x)}'")

mw.mainloop()
