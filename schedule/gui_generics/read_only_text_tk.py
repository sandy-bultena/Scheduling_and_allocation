from typing import Literal

from schedule.Tk import Scrolled

SCROLLBAR_DIR = Literal["s", "w", "e", "n", "se", "sw", "ne", "nw"]


class ReadOnlyTextTk:
    def __init__(self, frame, text: list[str] = None, height: int = 20, width: int = 50, scrollbars: SCROLLBAR_DIR = 'se',
                 wrap="none"):
        # remove any pre-existing widgets in this frame
        for w in frame.winfo_children():
            w.destroy()

        s: Scrolled = Scrolled(
            frame,
            'Text',
            height=height,
            width=width,
            scrollbars=scrollbars,
            wrap=wrap
        )
        s.pack(expand=True, fill="both")
        self.textbox = s.widget
        if text is not None:
            self.write(text)
        self.textbox.config(state="disabled")

    def write(self, text):
        self.textbox.config(state="normal")
        self.textbox.delete("1.0", "end")
        for txt in text:
            self.textbox.insert('end', txt + "\n")
        self.textbox.config(state="disabled")
