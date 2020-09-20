import tkinter as tk

# Frame IDs
DEFAULT = -1
MAIN = 0
BOOLEAN = 1
ENTRY = 2
INDEX_COLLAPSE = 3
INDEX_EXPAND_R = 4
INDEX_EXPAND_D = 5

# Set the number of elements (columns) per parameter. Currently three
# elements are used: name, info button, entry/checkbox
ELEMENTS_PER_PARAMETER = 3

class BlancFrame(tk.Frame):
    """
    Class for the blanc frame.
    """

    def __init__(self,parent,rows=1,columns=1,set_grid_propagate=True,
                 frame_id=-1,*args, **kwargs):
        """
        In the initialization of the blanc frame the number of rows,
        columns and the frame index can be defined. Finally the frame
        is placed into the parent.

        :param parent: tk widget, where this frame has to be placed
        :param rows: number of rows of the grid
        :param columns: number of columns of the grid
        :param frame_index: the index of the frame
        :param set_grid_propagate: parameter for the grid_propagate function
        :param args: is forwared to the super().__init__() function
        :param kwargs: is forwared to the super().__init__() function
        """
        super().__init__(parent,borderwidth=1,relief=tk.SUNKEN,
             width=890,*args,**kwargs)
        self.rows = rows
        self.columns = columns
        self.frame_id = frame_id
        self.update_grid_rowconfigure(frame_id)
        self.update_grid_columnconfigure(frame_id)
        self.grid_propagate(set_grid_propagate)
        self.grid(sticky="NESW")

    def update_grid_rowconfigure(self, frame_id):
        if self.rows > 0:
            if frame_id == INDEX_EXPAND_D:
                for i in range(self.rows):
                    self.grid_rowconfigure(i, weight=1)
                
                self.grid_rowconfigure(0,weight=0)                
            for i in range(self.rows):
                self.grid_rowconfigure(i, weight=1)


    def update_grid_columnconfigure(self, frame_id):
        # Update the frame id
        self.frame_id = frame_id
        if self.columns > 0:          
            # Set the weights for default BlancFrames (as used in the
            # welcome screen for instance)
            if self.frame_id == DEFAULT:
                self.grid_columnconfigure(0,weight=1)
                self.grid_columnconfigure(1,weight=1)
                self.grid_columnconfigure(2,weight=1)
            # Set the weights for the main content Frames in every tab
            if self.frame_id == MAIN:
                self.grid_columnconfigure(0,weight=1)
            # Set the weights for the BlancFrames holding the boolean
            # parameters
            elif self.frame_id == BOOLEAN:
                for i in range(0,self.columns,ELEMENTS_PER_PARAMETER):
                    # Move the last element in every row closer to the
                    # edge of the frame
                    if i == self.columns-3:
                        self.grid_columnconfigure(i, weight=1)
                        self.grid_columnconfigure(i+1, weight=1)
                        self.grid_columnconfigure(i+2, weight=5)
                    else:
                        self.grid_columnconfigure(i, weight=1)
                        self.grid_columnconfigure(i+1, weight=1)
                        self.grid_columnconfigure(i+2, weight=25)
            # Set the weights for the BlancFrames holding the entry 
            # parameters
            elif self.frame_id == ENTRY:
                for i in range(0,self.columns,ELEMENTS_PER_PARAMETER):
                    self.grid_columnconfigure(i, weight=1)
                    self.grid_columnconfigure(i+1, weight=1)
                    self.grid_columnconfigure(i+2, weight=20)
            # Set the weights for the BlancFrames holding the index
            # variable array parameters in collapsed format
            elif self.frame_id == INDEX_COLLAPSE:
                # Set the weight of the main label, the info button
                # and the entry
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                # Set the weight of all other columns
                for i in range(3,self.columns-2):
                    self.grid_columnconfigure(i, weight=10)
                # Set the weight of the two arrow buttons
                self.grid_columnconfigure(self.columns-1, weight=0)
                self.grid_columnconfigure(self.columns, weight=0)
            # Set the weights for the BlancFrames holding the index
            # variable array parameters in expanded format
            elif self.frame_id == INDEX_EXPAND_R:
                # Set the weight of the main label, the info button
                # and the entry
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=1)
                # Set the weight of all other columns
                for i in range(3,self.columns-2):
                    self.grid_columnconfigure(i, weight=1)
                # Set the weight of the two arrow buttons
                self.grid_columnconfigure(self.columns-1, weight=0)
                self.grid_columnconfigure(self.columns, weight=0)
