import tkinter as tk


class BlancFrame(tk.Frame):
    """
    class for the blanc frame
    """

    def __init__(self, parent, rows=1, columns=1, set_grid_propagate=True,
                 column_weight=1, *args, **kwargs):
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN, *args,
                         **kwargs)
        self.rows = rows
        self.columns = columns
        self.weight = column_weight
        self.update_grid_rowconfigure()
        self.update_grid_columnconfigure()
        self.grid_propagate(set_grid_propagate)
        self.grid(sticky="NESW")

    def update_grid_rowconfigure(self):
        if self.rows > 0:
            for i in range(self.rows):
                self.grid_rowconfigure(i, weight=1)

    def update_grid_columnconfigure(self):
        if self.columns > 0:
            for i in range(self.columns):
                self.grid_columnconfigure(i, weight=self.weight)
                self.columnconfigure(i, weight=self.weight)
