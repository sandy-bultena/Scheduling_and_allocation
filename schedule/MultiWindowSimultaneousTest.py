import tkinter as tk
import random

"""Sample code taken from StackOverflow which proves that multiple canvases can be updated at once, 
displaying the same things moving at the same speed at the same time.

Source: https://stackoverflow.com/a/7235679"""


class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.canvas1 = PeeredCanvas(self, width=300, height=300, border=1, relief="sunken")
        self.canvas2 = PeeredCanvas(self, width=300, height=300, border=1, relief="sunken")
        self.canvas3 = PeeredCanvas(self, width=300, height=300, border=1, relief="sunken")
        self.canvas1.add_peer(self.canvas2)
        self.canvas1.add_peer(self.canvas3)
        toolbar = tk.Frame(self)
        clear_button = tk.Button(self, text="Refresh", command=self.refresh)
        clear_button.pack(in_=toolbar, side="left")
        toolbar.pack(side="top", fill="x")
        self.canvas1.pack(side="left", fill="both", expand=True)
        self.canvas2.pack(side="left", fill="both", expand=True)
        self.canvas3.pack(side="left", fill="both", expand=True)
        self.animate(10)

    def animate(self, delay):
        '''Move all items down at a random rate'''
        for item in self.canvas1.find_all():
            delta_x = 0
            delta_y = random.randrange(1, 4)
            self.canvas1.move(item, delta_x, delta_y)
        self.after(delay, self.animate, delay)

    def refresh(self, count=100):
        '''Redraw 'count' random circles'''
        self.canvas1.delete("all")
        width = self.canvas1.winfo_width()
        height = self.canvas1.winfo_height()
        for i in range(count):
            if i % 2 == 0:
                tags = ("even",)
            else:
                tags = ("odd",)
            x = random.randrange(10, width - 10)
            y = random.randrange(10, height - 10)
            radius = random.randrange(10, 100, 10) / 2
            self.canvas1.create_oval([x, y, x + radius, y + radius], tags=tags)
        self.canvas1.itemconfigure("even", fill="red", outline="white")
        self.canvas1.itemconfigure("odd", fill="white", outline="red")


class PeeredCanvas(tk.Canvas):
    '''A class that duplicates all objects on one or more peer canvases'''

    def __init__(self, *args, **kwargs):
        self.peers = []
        tk.Canvas.__init__(self, *args, **kwargs)

    def add_peer(self, peer):
        if self.peers is None:
            self.peers = []
        self.peers.append(peer)

    def move(self, *args, **kwargs):
        tk.Canvas.move(self, *args, **kwargs)
        for peer in self.peers:
            peer.move(*args, **kwargs)

    def itemconfigure(self, *args, **kwargs):
        tk.Canvas.itemconfigure(self, *args, **kwargs)
        for peer in self.peers:
            peer.itemconfigure(*args, **kwargs)

    def delete(self, *args, **kwargs):
        tk.Canvas.delete(self, *args)
        for peer in self.peers:
            peer.delete(*args)

    def create_oval(self, *args, **kwargs):
        tk.Canvas.create_oval(self, *args, **kwargs)
        for peer in self.peers:
            peer.create_oval(*args, **kwargs)


app = SampleApp()
app.mainloop()
