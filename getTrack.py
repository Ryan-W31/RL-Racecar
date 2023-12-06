import tkinter as tk
from tkinter import ttk


class SketchTrack(tk.Canvas):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.bind("<Button-1>", self.getPosition, add="+")
        self.bind("<Button-1>", self.getInitPosition, add="+")
        self.bind("<B1-Motion>", self.draw)
        self.bind("<ButtonRelease-1>", self.stopDrawing)

        self.textId = self.create_text(
            980,
            100,
            text="Draw a racetrack! Make sure there are no loops!",
            anchor="n",
            font="TkMenuFont",
            fill="white",
        )

        self.redoButton = ttk.Button(self, text="Redo!", command=self.deleteTrack)
        self.redoButtonId = self.create_window(
            10, 10, anchor="nw", window=self.redoButton
        )

        self.okButton = ttk.Button(self, text="Done!", command=self.finishTrack)
        self.okButtonId = self.create_window(10, 50, anchor="nw", window=self.okButton)

        self.track = None
        self.initialFlag = True
        self.canvasFlag = True
        self.initialX, self.initialY = 0, 0

    def getInitPosition(self, event):
        if self.initialFlag and self.canvasFlag:
            self.initialX, self.initialY = event.x, event.y

        self.initialFlag = False

    def getPosition(self, event):
        self.prevX, self.prevY = event.x, event.y

    def draw(self, event):
        if self.canvasFlag:
            self.track = self.create_line(
                (self.prevX, self.prevY, event.x, event.y),
                fill="white",
                tags="trackId",
                smooth=True,
                splinesteps=20,
            )
            self.getPosition(event)

    def stopDrawing(self, event):
        if self.canvasFlag:
            self.create_line(
                (self.prevX, self.prevY, self.initialX, self.initialY),
                fill="white",
                tags="trackId",
                smooth=True,
                splinesteps=20,
            )

    def deleteTrack(self):
        self.delete("trackId")
        self.initialFlag = True
        self.canvasFlag = True

    def finishTrack(self):
        self.canvasFlag = False
        self.configure(state=tk.DISABLED)


app = tk.Tk()
app.geometry("1960x1080")

sketch = SketchTrack(app, bg="black")
sketch.pack(anchor="nw", fill="both", expand=1)

app.mainloop()
