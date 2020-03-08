import tkinter as tk


class BlancFrame(tk.Frame):
    """
    Class for the blanc frame.
    """

    def __init__(self, parent, rows=1, columns=1, set_grid_propagate=True, frame_index=-1,
                 *args, **kwargs):
        """
        In the initialization of the blanc frame the number of rows and
        columns can be defined, finally the frame is placed into the 
        parent.

        :param parent: tk widget, where this frame has to be placed
        :param rows: number of rows of the grid
        :param columns: number of columns of the grid
        :param set_grid_propagate: parameter for the grid_propagate function
        :param args: is forwared to the super().__init__() function
        :param kwargs: is forwared to the super().__init__() function
        """
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN, width=890, *args,
                         **kwargs)
        self.rows = rows
        self.columns = columns
        self.frame_index = frame_index
        self.update_grid_rowconfigure()
        self.update_grid_columnconfigure()
        self.grid_propagate(set_grid_propagate)
        self.grid(sticky="NESW")

    def update_grid_rowconfigure(self):
        if self.rows > 0:
            for i in range(self.rows):
                self.grid_rowconfigure(i, weight=1)
#                self.grid_rowconfigure(i+1, weight=0.1)
#                self.grid_rowconfigure(i+2, weight=1)

    def update_grid_columnconfigure(self):
        if self.columns > 0:          
#            for i in range(self.columns):
#                self.grid_columnconfigure(i, weight=1)
            if self.frame_index == 0:
                self.grid_columnconfigure(0,weight=1)
            elif self.frame_index == 1:
                for i in range(0,self.columns,3):
                    if i == self.columns-3:
                        self.grid_columnconfigure(i, weight=1)
                        self.grid_columnconfigure(i+1, weight=1)
                        self.grid_columnconfigure(i+2, weight=5)
                    else:
                        self.grid_columnconfigure(i, weight=1)
                        self.grid_columnconfigure(i+1, weight=1)
                        self.grid_columnconfigure(i+2, weight=25)
            elif self.frame_index == 2:
                for i in range(0,self.columns,3):
                    self.grid_columnconfigure(i, weight=1)
                    self.grid_columnconfigure(i+1, weight=1)
                    self.grid_columnconfigure(i+2, weight=20)
#            elif self.frame_index == 3:
##                for i in range(0,self.columns,3):
##                    self.grid_columnconfigure(i, weight=1)
##                    self.grid_columnconfigure(i+1, weight=1)
##                    self.grid_columnconfigure(i+2, weight=20)
#                for i in range(self.columns):
#                    self.grid_columnconfigure(i, weight=1)
#                
#                self.grid_columnconfigure(0, weight=1)
#                self.grid_columnconfigure(1, weight=1)
#                self.grid_columnconfigure(2, weight=1)
#                self.grid_columnconfigure(3, weight=1)
#                self.grid_columnconfigure(4, weight=1)
#                    self.grid_columnconfigure(i+1, weight=1)
#                    self.grid_columnconfigure(i+2, weight=1)