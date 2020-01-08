import tkinter as tk


class BlancCanvas(tk.Canvas):
    """
    Class for the blanc frame
    """

    def __init__(self, parent, rows=1, columns=1,
                 set_grid_propagate=False, *args, **kwargs):
        super().__init__(parent, highlightthickness=0, *args, **kwargs)
        self.grid_propagate(set_grid_propagate)
        self.set_num_of_rows(rows)
        self.set_num_of_columns(columns)
        self.grid(sticky="NESW")

    def set_num_of_rows(self, num_of_rows):
        if num_of_rows > 0:
            for i in range(num_of_rows):
                self.grid_rowconfigure(i, weight=1)

    def set_num_of_columns(self, num_of_columns):
        if num_of_columns > 0:
            for i in range(num_of_columns):
                self.grid_columnconfigure(i, weight=1)
