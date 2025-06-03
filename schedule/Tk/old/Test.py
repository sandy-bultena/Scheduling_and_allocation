from tkinter import *
from tkinter import ttk
from os import path
import sys
import re
from functools import partial

def get_parents(tree, tree_item_id: str) -> list[object]:
    return list(__get_parent(tree, tree.parent(tree_item_id)))


def __get_parent(tree, tree_item_id: str):
    while tree_item_id != "":
        yield tree_item_id
        tree_item_id = tree.parent(tree_item_id)

class StupidThing:
    def __init__(self,a):
        self.a = a
    def wtf(self):
        print (f"wtf {self.a}")
    def __str__(self):
        return f"Stringified {self.a}"

sys.path.append(path.dirname(path.dirname(__file__)))
from Scrolled import Scrolled

print(path.dirname(path.dirname(__file__)))

# make a Tk window
mw = Tk()
mw.geometry("500x300")

frame = Frame(mw)
frame.pack(expand=1, fill="both")
stv = Scrolled(frame, "Treeview")
stv.pack()
tv: ttk.Treeview = stv.widget
tv.configure(columns=("Object", "Type",), displaycolumns=("Object",))

x = tv.insert("", 'end', values=(StupidThing(1), "top"),)
y = tv.insert(x, 'end',  values=(StupidThing(15), "sub"),)
z = tv.insert(x, 'end', values=(StupidThing(16), "sub"),)
print("x values are:")
print("repr of x",repr(tv.item(x)))
b=tv.item(x)
b['obj'] = StupidThing(1)
print(b)
tv.item(x)["obj"] = StupidThing(1)
print("tv item x",tv.item(x))
#for v in tv.item(x)['values']:
#    print(repr(v))

button = Button(frame, text="Push me", command=lambda: tv.item(y, open=True))
button.pack(expand=1, fill='y')


def selectItem(e, *args):
    print("by mouse position", tv.identify_row(e.y))
    c = tv.identify_row(e.y)

    v = tv.item(c)
    tv.selection_set(c)
    print("getting selection")
    print(f"{v=}")
    print(f"Focused: {tv.item(c)['values']}")
    print(tv.item(c)['values'][0])
    #obj.wtf()
  #  print(f"values: {tv.item(v).values}")
  #  button.configure(text=v['text'])


for i in range(25):
    tv.insert(z, 'end', text=str(StupidThing(i)), values=(StupidThing(i),'sub'))
tv.item("", open=True)
tv.bind("<Button-2>", selectItem)
print(tv.item(z))
print(x)
print(tv.item(x))
print(tv.item(y))
xr = re.match(r"^=?(\d+)x(\d+)?([+-]\d+[+-]\d+)?$", frame.winfo_toplevel().geometry()).groups()

# does get_children return row-by-row?
# first insert new item in middle of all the z's, and then get children
tv.insert(z,15,text=str(StupidThing(101)))
for kid in tv.get_children(z):
    print (tv.item(kid)["text"])
# success :)


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
