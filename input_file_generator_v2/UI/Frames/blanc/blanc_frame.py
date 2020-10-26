import tkinter as tk

# FrameIDs used to set the proper weights of the widgets for each Frame
WELCOME = -2  # Welcome Window NR/NATOM Frame
DEFAULT = -1  # Default (used for the tabs)
MAIN = 0  # Main content Frame of the Imsil scroll Frame
BOOLEAN = 1  # The Frame holding the flags
ENTRY = 2  # The Frame holding the entries
# The index variable array Frames have 1 and 2 dimensional versions, 
# depending on the number of elements <-> the number of arrow Buttons
INDEX_COLLAPSE_1D = 3  # Index variable array Frame (collapsed state)
INDEX_COLLAPSE_2D = 4  # Index variable array Frame (collapsed state)
INDEX_EXPAND_R_1D = 5  # Index variable array Frame (expanded right)
INDEX_EXPAND_R_2D = 6  # Index variable array Frame (expanded right)
INDEX_EXPAND_D_1D = 7  # Index variable array Frame (expanded down)
INDEX_EXPAND_D_2D = 8  # Index variable array Frame (expanded down)
INDEX_EXPAND_RD = 9  # Index variable array Frame (expanded right&down)

# Set the number of elements (columns) per parameter. Currently three
# elements are used: name, info button, entry/checkbox
ELEMENTS_PER_PARAMETER = 3

class BlancFrame(tk.Frame):
    """
    Class for the blanc frame.
    """    
    def __init__(self, parent, rows=1, columns=1, frame_id=DEFAULT, 
                 set_grid_propagate=True, *args, **kwargs):
        """
        In the initialization of the BlancFrame the number of rows,
        columns and the FrameID can be defined. Finally the frame is
        placed into the parent.

        :param parent: the parent tk widget
        :param rows: number of rows of the grid
        :param columns: number of columns of the grid
        :param frame_id: the ID of the Frame
        :param set_grid_propagate: parameter for the grid_propagate 
                                   function
        :param args: is forwarded to the super().__init__() function
        :param kwargs: is forwarded to the super().__init__() function
        """
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN, 
                         width=890, *args, **kwargs)
        self.rows = rows
        self.columns = columns
        self.frame_id = frame_id
        self.update_grid_rowconfigure(frame_id)
        self.update_grid_columnconfigure(frame_id)
        self.grid_propagate(set_grid_propagate)
        self.grid(sticky="NESW")

    def update_grid_rowconfigure(self, frame_id):
        if self.rows > 0:            
            for i in range(self.rows):
                self.grid_rowconfigure(i, weight=1)

    def update_grid_columnconfigure(self, frame_id):
        # Update the frame id
        self.frame_id = frame_id

        if self.columns > 0:          
            # Set the weights for the default BlancFrames
            if self.frame_id == DEFAULT:
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=1)
            # Set the weights for the Welcome BlancFrames
            elif self.frame_id == WELCOME:
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                self.grid_columnconfigure(3, weight=1)
            # Set the weights for the main content Frames in every tab
            elif self.frame_id == MAIN:
                self.grid_columnconfigure(0, weight=1)
            # Set the weights for the Booelan BlancFrames
            elif self.frame_id == BOOLEAN:
                for i in range(0, self.columns, ELEMENTS_PER_PARAMETER):
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
            # Set the weights for the Entry BlancFrames 
            elif self.frame_id == ENTRY:
                for i in range(0, self.columns, ELEMENTS_PER_PARAMETER):
                    self.grid_columnconfigure(i, weight=1)
                    self.grid_columnconfigure(i+1, weight=1)
                    self.grid_columnconfigure(i+2, weight=20)
            # Set the weights for the index variable array BlancFrames
            elif self.frame_id == INDEX_COLLAPSE_1D:
                # Set the weight of the main Label, the Info Button
                # and the Entry
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                # Set the weight of all other columns
                for i in range(3, self.columns-1):
                    self.grid_columnconfigure(i, weight=10)
                # Set the weight of the arrow Button
                self.grid_columnconfigure(self.columns-1, weight=0)
            elif self.frame_id == INDEX_COLLAPSE_2D:
                # Set the weight of the main Label, the Info Button
                # and the Entry
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                # Set the weight of all other columns
                for i in range(3, self.columns-2):
                    self.grid_columnconfigure(i, weight=10)
                # Set the weight of the two arrow Buttons
                self.grid_columnconfigure(self.columns-2, weight=0)
                self.grid_columnconfigure(self.columns-1, weight=0)
            elif self.frame_id == INDEX_EXPAND_R_1D:
                # Set the weight of the main Label, the Info Button,
                # the Entry and the parameter Label
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                self.grid_columnconfigure(3, weight=0)
                # Set the weight of all other columns
                for i in range(4, self.columns-1):
                    self.grid_columnconfigure(i, weight=100)
                # Set the weight of the arrow Button
                self.grid_columnconfigure(self.columns-1, weight=0)
            elif self.frame_id == INDEX_EXPAND_R_2D:
                # Set the weight of the main Label, the Info Button,
                # the Entry and the parameter Label
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                self.grid_columnconfigure(3, weight=0)
                # Set the weight of all other columns
                for i in range(4, self.columns-2):
                    self.grid_columnconfigure(i, weight=100)
                # Set the weight of the two arrow Buttons
                self.grid_columnconfigure(self.columns-2, weight=0)
                self.grid_columnconfigure(self.columns-1, weight=0)
            elif self.frame_id == INDEX_EXPAND_D_1D:
                # Set the weight of the main Label, the Info Button,
                # the Entry and the parameter Label
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                self.grid_columnconfigure(3, weight=0)
                # Set the weight of all other columns
                for i in range(4, self.columns-1):
                    self.grid_columnconfigure(i, weight=100)
                # Set the weight of the two arrow buttons
                self.grid_columnconfigure(self.columns-1, weight=0)
            elif self.frame_id == INDEX_EXPAND_D_2D:
                # Set the weight of the main Label, the Info Button
                # and the Entry
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                # Set the weight of the first two param columns
                self.grid_columnconfigure(3, weight=0)
                self.grid_columnconfigure(4, weight=40)
                # Set the weight of all other columns
                for i in range(5, self.columns-2):
                    self.grid_columnconfigure(i, weight=100)
                # Set the weight of the two arrow Buttons
                self.grid_columnconfigure(self.columns-1, weight=0)
                self.grid_columnconfigure(self.columns, weight=0)
            elif self.frame_id == INDEX_EXPAND_RD:
                # Set the weight of the main Label, the Info Button,
                # the Entry and the parameter Label
                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=1)
                self.grid_columnconfigure(2, weight=0)
                self.grid_columnconfigure(3, weight=0)
                # Set the weight of all other columns
                for i in range(4, self.columns-2):
                    self.grid_columnconfigure(i, weight=100)
                # Set the weight of the two arrow buttons
                self.grid_columnconfigure(self.columns-2, weight=0)
                self.grid_columnconfigure(self.columns-1, weight=0)
