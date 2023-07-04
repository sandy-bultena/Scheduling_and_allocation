from tkinter import *
mw = Tk()
d=mw.keys()
print(d)
b=Button(mw)
print()
print ("BUTTON")
for k in b.keys():
    print(f"{k}:{b.cget(k)}")

t=Text(mw)
print()
print ("Text")
for k in t.keys():
    print(f"{k}:{t.cget(k)}")

d=Entry(mw)
print()
print("Entry")
for k in t.keys():
    print(f"{k}:{t.cget(k)}")
