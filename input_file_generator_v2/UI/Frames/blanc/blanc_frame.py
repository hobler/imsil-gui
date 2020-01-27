import tkinter as tk


class BlancFrame(tk.Frame):
    """
    Class for the blanc frame.
    """

    def __init__(self, parent, rows=1, columns=1, set_grid_propagate=True,
                 column_weight=1, *args, **kwargs):
        """
        In the initialization of the blanc frame the number of rows and
        columns can be defined, finally the frame is placed into the 
        parent.

        :param parent: tk widget, where this frame has to be placed
        :param rows: number of rows of the grid
        :param columns: number of columns of the grid
        :param set_grid_propagate: parameter for the grid_propagate function
        :param column_weight: the weight of the columns
        :param args: is forwared to the super().__init__() function
        :param kwargs: is forwared to the super().__init__() function
        """
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
