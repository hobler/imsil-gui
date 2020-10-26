"""
This module defines several tk.Frames and creates a row for each 
parameter with the following elements: 
    - a tk.Label with the parameter name, 
    - an Info Button which displays the short description of the 
      parameter when hovered and opens a window with the long
      description when clicked
    - a tk.Entry that contains the parameter value (or a tk.Checkbutton
      if the parameter is of type boolean)
    - arrows that allow to expand the array for parameters of the type
      index variable array
"""

import platform
import Pmw
import tkinter as tk
from tkinter import messagebox

from DataModel.DataList import DataList
from UI.Canvas.blanc.blanc_canvas import BlancCanvas
from UI.Frames.blanc.blanc_frame import BlancFrame
from UI.Frames.blanc.blanc_frame import MAIN as MAIN
from UI.Frames.blanc.blanc_frame import BOOLEAN as BOOLEAN
from UI.Frames.blanc.blanc_frame import ENTRY as ENTRY
from UI.Frames.blanc.blanc_frame import INDEX_COLLAPSE_1D as INDEX_COLLAPSE_1D
from UI.Frames.blanc.blanc_frame import INDEX_COLLAPSE_2D as INDEX_COLLAPSE_2D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_R_1D as INDEX_EXPAND_R_1D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_R_2D as INDEX_EXPAND_R_2D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_D_1D as INDEX_EXPAND_D_1D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_D_2D as INDEX_EXPAND_D_2D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_RD as INDEX_EXPAND_RD

OS = platform.system()

# Configure the width and height of the widgets
INFO_WIDTH = 10 # Info Button width
INFO_HEIGHT = 10 # Info Button height
ARROW_WIDTH = 20 # Width of the arrow (and '+'/'-') Button(s)
ARROW_HEIGHT = 20 # Height of the arrow (and '+'/'-') Button(s)

# Width of the parameter name field for index variable arrays. The use
# of a width is necessary, since every parameter has a separate frame
# and thus they can't be aligned by only using weights
INDEX_NAME_WIDTH = 8

# Number of parameters per row for each type of parameter
BOOL_PARAMS_PER_ROW = 4
ENTRY_PARAMS_PER_ROW = 2
INDEX_PARAMS_PER_ROW = 1
# Number of elements (columns) per parameter. Currently three
# elements are used: Label, Info Button, Entry/Checkbox
ELEMENTS_PER_PARAM = 3

# The number of fixed elements for index variable array parameters:
# 1 Label & 1 Info Button (+ Entry turned on & off)
NUM_ELEMS = 2 


class ImsilScrollFrame(BlancFrame):
    """
    In the initialization the scrollable area and the content Frames
    for each type of parameter are created.
    """
    def __init__(self, parent, nr=3, natom=2, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)    
            
        # Assign the number of Regions and Atoms
        self.n_r = nr.get()
        self.n_atom = natom.get()

        # Define the number of columns for the boolean and entry 
        # parameters
        self.columns_b = BOOL_PARAMS_PER_ROW * ELEMENTS_PER_PARAM
        self.columns_e = ENTRY_PARAMS_PER_ROW * ELEMENTS_PER_PARAM
        # The number of columns for index variable arrays as well as 
        # the Frames for each index variable array parameter are 
        # created dynamically

        # Initialize the counter variable to track the number of 
        # parameters in the current row
        self.params_in_row = 0
        # Initialize the counter variables for each type of parameter
        self.num_bools = 0
        self.num_entries = 0
        self.num_index = 0
        self.num_points = 1

        # Create the lists holding the Frames
        self.par_frame_list = []
        self.ui_data_list = DataList()

        # Build the scrolling area
        self.main_canvas = BlancCanvas(self, columns=1, width=890)
        self.content_frame = BlancFrame(self.main_canvas, frame_id=MAIN)
        # @create_window: parameter 'tags' is later required to change
        # the window size
        self.main_canvas.create_window(0, 0,
                                       window=self.content_frame,
                                       tags="self.content_frame", 
                                       anchor="nw")
        self.vertical_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="NES")
        self.vertical_scrollbar.config(command=self.main_canvas.yview)
        self.main_canvas.config(yscrollcommand=self.vertical_scrollbar.set)
        self.bind_mouse_event(self.content_frame)

        # Use a separate Frame for boolean and entry type parameters
        self.content_frame_bool = BlancFrame(self.content_frame,
                                             columns=self.columns_b,
                                             frame_id=BOOLEAN)
        self.content_frame_bool.grid(sticky="NESW")
        
        self.content_frame_entry = BlancFrame(self.content_frame,
                                              columns=self.columns_e,
                                              frame_id=ENTRY)
        self.content_frame_entry.grid(sticky="NESW")

        # Add the two frames to the list of frames
        self.par_frame_list.append(self.content_frame_bool)
        self.par_frame_list.append(self.content_frame_entry)

        # Update the UI
        self.content_frame.update_idletasks()
        self.content_frame.bind("<Configure>", self.update_scrollregion)
        self.main_canvas.bind('<Configure>', self.update_frame_width)

    def update_frame_width(self, event):
        """
        Is automatically called, if window is resized
        
        :param event: the event, which gets triggered by resizing
        """
        self.main_canvas.itemconfig("self.content_frame", width=event.width)

    def update_scrollregion(self, event):
        """
        Is automatically called at scrolling
        
        :param event: the event, which gets triggered by resizing
        """
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def update_buttons_command(self, par_frame_index, index_var_list):
        """
        Update the commands assigned to the different buttons.
        
        Go through each widget in the specified Frame and update the 
        commands assigned to the Buttons, based on their text. 
        
        :param par_frame_index: the index of the parent Frame
        :param index_var_list: the List of index variable elements for
                               the current parameter
        """
        par_frame = self.par_frame_list[par_frame_index]
        for child in par_frame.winfo_children():
            if child.winfo_class() == 'Button':
                # If the Button is not placed within the grid yet, do
                # not handle it
                if not child.grid_info():
                    continue
                child_grid_row = child.grid_info()['row']
                
                # If it is a down arrow Button (marked with 'd')
                if 'd' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.open_index_var_d(par_frame_index=par_frame_index,
                                              index_var_list=index_var_list,
                                              row_index=row_index))
                # If it is an up arrow Button (marked with 'u')
                if 'u' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.close_index_var_u(par_frame_index=par_frame_index,
                                               index_var_list=index_var_list,
                                               row_index=row_index))
                # If it is a right arrow Button (marked with 'r')
                if 'r' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.open_index_var_r(par_frame_index=par_frame_index,
                                              index_var_list=index_var_list,
                                              row_index=row_index))
                # If it is a left arrow Button (marked with 'l')
                if 'l' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.close_index_var_l(par_frame_index=par_frame_index,
                                               index_var_list=index_var_list,
                                               row_index=row_index))
                # If it is a + Button (marked with '+')
                if '+' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.add_row(par_frame_index=par_frame_index,
                                     index_var_list=index_var_list,
                                     row_index=row_index)) 
                # If it is a - Button (marked with '-')
                if '-' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.delete_row(par_frame_index=par_frame_index,
                                        index_var_list=index_var_list,
                                        row_index=row_index)) 

    def get_dimensions(self, par_frame, index_var_list):
        """
        Get the dimensions of the index variable array to be created.
        
        Get the dimensions of the index variable array, depending on 
        the number of parameters in the index_var_list. Additionally,
        consider the parameters themselves, to decide .
        
        :param par_frame_index: the index of the parent Frame
        :param index_var_list: the List of index variable elements for
                               the current parameter
        """
        IS_POINT = False
        # Get the number of elements for the current parameter
        dim = len(index_var_list)
        # Set the number of rows and columns of the array
        if dim == 1:
            if "ATOM1" in index_var_list or "ATOM2" in index_var_list:
                # Create a 1 x NATOM array
                m = 1
                n = self.n_atom
            elif "REGION" in index_var_list and "geom" in str(par_frame):
                # Create an NR x 1 array in the geom tab
                m = self.n_r
                n = 1
            elif "REGION" in index_var_list:
                # Create a 1 x NR array
                m = 1
                n = self.n_r
            elif "POINT" in index_var_list:
                # Create a special array for POINT
                IS_POINT = True
                m = self.num_points
                n = 2
        elif dim == 2:
            if ("REGION" in index_var_list and 
                ("ATOM1" in index_var_list or "ATOM2" in index_var_list)):
                # Create an NR x NATOM array
                m = self.n_r
                n = self.n_atom
            elif "ATOM1" in index_var_list and "ATOM2" in index_var_list:
                # Create an NATOM x NATOM array
                m = self.n_atom
                n = self.n_atom
                
        return (dim, m, n, IS_POINT)
    
    def get_state(self, par_frame, text):
        """
        This method is used to get the current state of an index
        variable array as well as the reference to the desired button.
        
        :param par_frame: the parent Frame
        :param text: the text to identify the Button (e.g. 'r')
        """
        IS_DOWN = False
        IS_RIGHT = False
        
        for widget in par_frame.children.values():
            if widget.winfo_class() == "Button" :
                # Down Button is visible -> array is collapsed
                if 'd' == widget.cget('text'):
                    IS_DOWN = False
                    if 'd' == text:
                        desired_button = widget
                # Up Button is visible -> the array is expanded
                elif 'u' == widget.cget('text'):
                    IS_DOWN = True
                    if 'u' == text:
                        desired_button = widget
                # Right Button is visible -> array is collapsed
                if 'r' == widget.cget('text'):
                    IS_RIGHT = False
                    if 'r' == text:
                        desired_button = widget
                # Left Button is visible -> the array is expanded
                elif 'l' == widget.cget('text'):
                    IS_RIGHT = True
                    if 'l' == text:
                        desired_button = widget
                    
        return (desired_button, IS_DOWN, IS_RIGHT)
    
    def set_button(self, widget, file, text):
        """
        Set the Button with the text and picture specified.
                
        This method sets the Button image and text. It is used to set
        up the Buttons initially as well as to swap the Buttons 
        (up <-> down & right <-> left) after the user pressed them. 
        
        :param widget: the Button to be set
        :param file: the name of the new image file
        :param text: the new text of the Button (for identification)
        """
        btn_new = widget
        self.photo_new = tk.PhotoImage(file=file)
        btn_new.config(image=self.photo_new)
        btn_new.image = self.photo_new;
        btn_new.config(takefocus=False)
        btn_new.config(text=text)
    
    def set_weights(self, par_frame, dim, IS_DOWN, IS_RIGHT, IS_POINT):
        """
        Set the weights of the index variable arrays, using the presets
                
        Set the weights of the Frames, depending on their dimensions 
        and their state: collapsed/expanded(right)/expanded(down)/
        expanded(right&down). 
        
        :param par_frame_index: the index of the parent Frame
        :param dim: the number of index variable elements
        :param IS_DOWN: True if the array is expanded downwards
        :param IS_RIGHT: True if the array is expanded to the right
        :param IS_POINT: True if the parameter is POINTS (special array)
        """
        # If the array is for POINTS (special array)
        if IS_POINT:
            if IS_DOWN:
                par_frame.update_grid_columnconfigure(INDEX_EXPAND_RD)
            else:
                par_frame.update_grid_columnconfigure(INDEX_COLLAPSE_2D)
        # If it is a normal 1D array
        elif dim == 1:
            if IS_DOWN:
                par_frame.update_grid_columnconfigure(INDEX_EXPAND_D_1D)
            elif IS_RIGHT:
                par_frame.update_grid_columnconfigure(INDEX_EXPAND_R_1D)
            else:
                par_frame.update_grid_columnconfigure(INDEX_COLLAPSE_1D)
        # If it is a normal 2D array
        elif dim == 2:
            if IS_DOWN and IS_RIGHT:
                par_frame.update_grid_columnconfigure(INDEX_EXPAND_RD)
            elif IS_DOWN:
                par_frame.update_grid_columnconfigure(INDEX_EXPAND_D_2D)
            elif IS_RIGHT:
                par_frame.update_grid_columnconfigure(INDEX_EXPAND_R_2D)
            else:            
                par_frame.update_grid_columnconfigure(INDEX_COLLAPSE_2D)

    def set_entry_values(self, par_frame):
        """
        This method is used to set the values of the index variable
        array elements to match the value of the single Entry
        
        :param par_frame: the parent Frame
        """
        # Iterate through every widget, and change their value, to
        # match the value of the single Entry
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info button
            if i < NUM_ELEMS:
                continue
            # Get the value of the single Entry
            elif i == NUM_ELEMS:
                curr_val = widget.get()
            # Set the value of all other Entry widgets
            elif (curr_val != "Multiple values" and 
                  widget.winfo_class() == "Entry"):
                widget.delete(0, "end")  # Delete
                widget.insert(0, curr_val)  # Readd 
                
    def set_entry_value(self, par_frame, m, n):
        """
        This method is used to set the value of the single Entry to 
        match the value of the index variable array elements
        
        :param par_frame: the parent Frame
        :param m: the number of rows of the index variable array
        :param n: the number of columns of the index variable array
        """
        items = []
        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and Info Button
            if i < NUM_ELEMS:
                continue
            # Get the reference of the single Entry
            elif i == NUM_ELEMS:
                curr_widget = widget
            # Get the value of all other Entry widgets
            elif (i < (NUM_ELEMS+1) + (m+1)*(n+1) and 
                      widget.winfo_class() == "Entry"):
                items.append(widget.get())  # Delete

        curr_widget.delete(0, "end")  # Delete
        # If all values are the same
        if all(items[0] == item for item in items):                
            curr_widget.insert(0, items[0])  # Readd 
        else:
            curr_widget.insert(0, "Multiple values")  # Readd

    def hide_widgets(self, par_frame, m, n, showEntry=False, row_index=None):
        """
        This method is used to hide the widgets in the index variable
        array of the specified Frame.
        
        :param par_frame: the parent Frame
        :param m: the number of rows of the index variable array
        :param n: the number of columns of the index variable array
        :param showEntry: the option to show the Entry (off by default)
        :param row_index: the number of columns of the index variable array
        """
        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info button
            if i < NUM_ELEMS:
                continue
            # Show the single Entry if the option is set
            elif i == NUM_ELEMS and showEntry:
                widget.grid(row=row_index, column=NUM_ELEMS, sticky="NESW")
            # Hide all other elements (except the two arrow Buttons)
            elif i < (NUM_ELEMS+1) + (m+1)*(n+1):
                widget.grid_forget()

    def open_index_var_r(self, par_frame_index, index_var_list, row_index):
        """
        This method is used to expand the array of an index variable
        array parameter horizontally/to the right.
        
        :param par_frame_index: the index of the parent Frame
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Assign the corresponding frame    
        par_frame = self.par_frame_list[par_frame_index]
        # Get the Button reference and array state
        right_arrow_btn, IS_DOWN, IS_RIGHT = self.get_state(par_frame, 'r')
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(par_frame, index_var_list)

        # If the array is collapsed currently
        if not IS_DOWN:
            # Set the Entry values to match the single Entry
            self.set_entry_values(par_frame)
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()
                # Show the first row with the header
                elif i < ((NUM_ELEMS+1) + (n+1)):
                    widget.grid(row=0, column=i, sticky="NESW")
                # Show the second row with the values
                elif i < ((NUM_ELEMS+1) + 2*(n+1)):
                    widget.grid(row=1, column=i - (n+1), sticky="NESW")
        # If the array is expanded downwards
        else:
            # Hide every widget except the main Label and Info Button
            self.hide_widgets(par_frame, m, n)
            # Iterate through every widget, and readd them
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label, the Info Button and the Entry
                if i <= NUM_ELEMS:
                    continue
                # Show all other widgets
                elif i < (NUM_ELEMS+1) + (m+1)*(n+1):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (n+1)
                    curr_col = i - curr_row*(n+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, sticky="NESW")
                
        # Change the right arrow button to a left arrow button
        self.set_button(right_arrow_btn, "arrow_l.gif", "l")
        # Update the Button commands
        self.update_buttons_command(par_frame_index, index_var_list)
        # Set the weigths for the new state
        self.set_weights(par_frame, dim, IS_DOWN, True, IS_POINT)
        
    def close_index_var_l(self, par_frame_index, index_var_list, row_index):
        """
        This method is used to collapse the array of an index variable
        array parameter horizontally/to the left.
                
        :param par_frame_index: the index of the parent Frame
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Assign the corresponding frame 
        par_frame = self.par_frame_list[par_frame_index]
        # Get the Button reference and array state
        left_arrow_btn, IS_DOWN, IS_RIGHT = self.get_state(par_frame, 'l')
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(par_frame, index_var_list)

        # Hide every widget except the main Label and Info Button and
        # show the Entry
        self.hide_widgets(par_frame, m, n, True, row_index)                
        # If the array is expanded downwards readd the widgets
        if IS_DOWN:
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label, the Info Button and the Entry
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()
                elif (i < (NUM_ELEMS+1) + (m+1)*(n+1) and 
                      ((i - (NUM_ELEMS+1)) % (n+1) == 0 or 
                       (i - (NUM_ELEMS+1)) % (n+1) == 1)):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (n+1)
                    curr_col = i - curr_row*(n+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, sticky="NESW")
        # Otherwise check, if all Entry values are the same
        else:
            self.set_entry_value(par_frame, m, n)
            
        # Change the left arrow button to the right arrow button
        self.set_button(left_arrow_btn, "arrow_r.gif", "r")
        # Update the Button commands
        self.update_buttons_command(par_frame_index, index_var_list)
        # Set the weigths for the new state
        self.set_weights(par_frame, dim, IS_DOWN, False, IS_POINT)
            
    def open_index_var_d(self, par_frame_index, index_var_list, row_index):
        """
        This method is used to expand the array of an index variable
        array parameter vertically/down.
                        
        :param par_frame_index: the index of the parent Frame
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Assign the corresponding frame    
        par_frame = self.par_frame_list[par_frame_index]
        # Get the Button reference and array state
        down_arrow_btn, IS_DOWN, IS_RIGHT = self.get_state(par_frame, 'd')
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(par_frame, index_var_list)

        # If the array is collapsed currently    
        if not IS_RIGHT:
            # Set the Entry values to match the single Entry
            self.set_entry_values(par_frame)
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()
                elif (i < (NUM_ELEMS+1) + (m+1)*(n+1) and 
                      ((i - (NUM_ELEMS+1)) % (n+1) == 0 or 
                       (i - (NUM_ELEMS+1)) % (n+1) == 1 or
                       (((i - (NUM_ELEMS+1)) % (n+1) == 2) and IS_POINT))):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (n+1)
                    curr_col = i - curr_row*(n+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, sticky="NESW")
        # If the array is expanded to the right
        else:
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()
                # Show all other widgets below the 2nd row (the widgets
                # in the first and second row are visible already)
                elif (i >= ((NUM_ELEMS+1) + 2*(n+1)) and
                      i < (NUM_ELEMS+1) + (m+1)*(n+1)):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (n+1)
                    curr_col = i - curr_row*(n+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, sticky="NESW")
                
        # Change the down arrow button to an up arrow button
        self.set_button(down_arrow_btn, "arrow_u.gif", "u")
        # Update the Button commands
        self.update_buttons_command(par_frame_index, index_var_list)
        # Set the weigths for the new state
        self.set_weights(par_frame, dim, True, IS_RIGHT, IS_POINT)

    def close_index_var_u(self, par_frame_index, index_var_list, row_index):
        """
        This method is used to collapse the array of an index variable
        array parameter vertically/up.
                        
        :param par_frame_index: the index of the parent Frame
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Assign the corresponding frame 
        par_frame = self.par_frame_list[par_frame_index]
        # Get the Button reference and array state
        up_arrow_btn, IS_DOWN, IS_RIGHT = self.get_state(par_frame, 'u')
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(par_frame, index_var_list)

        # Hide every widget except the main Label and Info Button and
        # show the Entry
        self.hide_widgets(par_frame, m, n, True, row_index)                  
        # If the array is expanded to the right, readd the widgets
        if IS_RIGHT:
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()
                # Show the first row with the Header for the Atoms
                elif i < ((NUM_ELEMS+1) + (n+1)):
                    widget.grid(row=0, column=i, sticky="NESW")
                # Show the second row with the Label for the Region and
                # the Entries for the Atoms
                elif i < ((NUM_ELEMS+1) + 2*(n+1)):
                    widget.grid(row=1, column=i-(n+1), sticky="NESW")
        # Otherwise check, if all Entry values are the same
        else:
            self.set_entry_value(par_frame, m, n)
                
        # Change the up arrow button to the down arrow button
        self.set_button(up_arrow_btn, "arrow_d.gif", "d")
        # Update the Button commands
        self.update_buttons_command(par_frame_index, index_var_list)
        # Set the weigths for the new state
        self.set_weights(par_frame, dim, False, IS_RIGHT, IS_POINT)

    def add_row(self, par_frame_index, index_var_list, row_index):
        """
        This method is used to add a row for index variable arrays
        for the POINT parameter.
                        
        :param par_frame_index: the index of the parent Frame
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Assign the corresponding frame    
        par_frame = self.par_frame_list[par_frame_index]
        
        # Iterate through every widget
        for widget in par_frame.children.values():
            if widget.winfo_class() == "Button" :
                # If the down Button is visible, the array is collapsed
                if 'd' == widget.cget('text'):
                    btn_down = widget
                    IS_DOWN = False
                # If the up Button is visible, the array is expanded
                elif 'u' == widget.cget('text'):
                    btn_up = widget
                    IS_DOWN = True
                elif '+' == widget.cget('text'):
                    btn_add = widget
    
        # Delete the Buttons and readd them later, so they are always 
        # the last elements when iterating through the children widgets
        btn_add.destroy()
        if IS_DOWN:
            btn_up.destroy()
        else:
            btn_down.destroy()
        
        # Increase the counter variable value
        self.num_points += 1
        
        # Add the row with a Label and Entry
        self.add_label(parent=par_frame, 
                       label_text="POINT " + str(self.num_points))
        self.add_entry(parent=par_frame, par_name='POS', 
                       entry_text="", add_to_list = False)
        # Add the remove Button
        button_remove = self.add_button(parent=par_frame, btn_text="-",
                                   w=ARROW_WIDTH, h=ARROW_HEIGHT)
        self.set_button(button_remove, "minus.gif", '-')
                    
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(par_frame, index_var_list)
        
        # Add the '+' and the down/up arrow Button
        button_add = self.add_button(parent=par_frame, btn_text="+",
                                   w=ARROW_WIDTH, h=ARROW_HEIGHT)
        self.set_button(button_add, "add.gif", '+')
        button_add.grid(row=row_index ,column=7 - 2)
         
        button_arrow = self.add_button(parent=par_frame, btn_text="",
                                       w=ARROW_WIDTH, h=ARROW_HEIGHT)
        if IS_DOWN:            
            self.set_button(button_arrow, "arrow_u.gif", 'u')            
        else:
            self.set_button(button_arrow, "arrow_d.gif", 'd')
            
        button_arrow.grid(row=row_index ,column=7 - 1)
            
        # If the array is expanded downwards
        if IS_DOWN:
            # Hide every widget except the main Label and Info Button
            self.hide_widgets(par_frame, m, n)
            # Iterate through every widget, and readd them
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label, the Info Button and the Entry
                if i <= NUM_ELEMS:
                    continue
                # Show all other widgets
                elif i < (NUM_ELEMS+1) + (m+1)*(n+1):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (n+1)
                    curr_col = i - curr_row*(n+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, sticky="NESW")
                        
        # Update the Button commands
        self.update_buttons_command(par_frame_index, index_var_list)
        # Set the weigths for the new state
        self.set_weights(par_frame, dim, IS_DOWN, False, True)
            
    def delete_row(self, par_frame_index, index_var_list, row_index):
        """
        This method is used to delete a row for index variable arrays
        for the POINT parameter.
                        
        :param par_frame_index: the index of the parent Frame
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Assign the corresponding frame
        par_frame = self.par_frame_list[par_frame_index]
        
        # Iterate through every widget
        for widget in par_frame.children.values():
            if not widget.grid_info():
                continue  # Skip widgets that are not placed
            elif widget.grid_info()['row'] == row_index:
                if widget.winfo_class() == "Label":
                    curr_label = widget
                elif widget.winfo_class() == "Entry":
                    curr_entry = widget
                elif widget.winfo_class() == "Button":
                    curr_button = widget
            elif widget.grid_info()['row'] > row_index:
                break  # Only consider widgets from the specified row
            
        # Delete the widgets of the specified row
        curr_label.destroy()
        curr_entry.destroy()
        curr_button.destroy()

        # Decrease the counter variable value
        self.num_points -= 1       
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(par_frame, index_var_list)
 
        # Hide every widget except the main Label and Info Button
        self.hide_widgets(par_frame, m, n)
        # Iterate through every widget, and readd them
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label, the Info Button and the Entry
            if i <= NUM_ELEMS:
                continue
            # Show all other widgets
            elif i < (NUM_ELEMS+1) + (m+1)*(n+1):
                # Calculate the current row and column
                curr_row = (i - (NUM_ELEMS+1)) // (n+1)
                curr_col = i - curr_row*(n+1)
                # Place the widget
                widget.grid(row=curr_row, column=curr_col, sticky="NESW")

        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):
            if i < NUM_ELEMS+5 or not widget.grid_info():
                continue            
            elif (widget.winfo_class() == "Label" and 
                  "POINT" in widget.cget('text')):
               widget.config(text=('POINT ' + str(widget.grid_info()['row'])))

        # Update the Button commands
        self.update_buttons_command(par_frame_index, index_var_list)

    def add_content_in_par_frame(self, par_name, index_var_list, default_value,
                                 short_desc, long_desc, is_bool, is_index_var,
                                 row_index):                
        """
        Add the parameter to the corresponding content Frame.

        :par_name: parameter name
        :index_var_list: a list of index variables that are used by this
                         parameter
        :default_value: default value of the parameter
        :short_desc: short description of the parameter
        :long_desc: long description of the parameter
        :is_bool: true, if the parameter is of type bool, false else
        :is_index_var: true, if the parameter is of type bool, false else
        :row_index: row number where the new parameter should be placed
        """          
        # Check the type of the parameter
        if is_index_var:    
            # Get the number of elements for the current parameter
            dim = len(index_var_list)
            # Set the number of rows and columns of the array
            if dim == 1:
                curr_frame_id = INDEX_COLLAPSE_1D
                if "ATOM1" in index_var_list or "ATOM2" in index_var_list:
                    # Create a 1 x NATOM array
                    num_rows = 2  # Header+Value
                    num_columns = 5 + self.n_atom  # 3Fix+Header+Button
                elif ("REGION" in index_var_list and 
                      "geom" in str(self.content_frame)):
                    # Create an NR x 1 array
                    num_rows = 1 + self.n_r  # Header+nr rows
                    num_columns = 5 + 1  # 3Fix+Header+Button+Column
                elif "REGION" in index_var_list:
                    # Create a 1 x NR array
                    num_rows = 2  # Header+Value
                    num_columns = 5 + self.n_r  # 3Fix+Header+Button
                elif "POINT" in index_var_list:
                    curr_frame_id = INDEX_COLLAPSE_2D
                    # Create a special array for POINT
                    num_rows = 2  # Header+Value
                    num_columns = 6 + 1  # 3Fix+Header+2Button+Column
            elif dim == 2:
                curr_frame_id = INDEX_COLLAPSE_2D
                if ("REGION" in index_var_list and 
                    ("ATOM1" in index_var_list or "ATOM2" in index_var_list)):
                    # Create an NR x NATOM array
                    num_rows = 1 + self.n_r  # Header+nr rows
                    num_columns = 6 + self.n_atom # 3Fix+Header+2Button
                elif "ATOM1" in index_var_list and "ATOM2" in index_var_list:
                    # Create an NATOM x NATOM array
                    num_rows = 1 + self.n_atom  # Header+natom rows
                    num_columns = 6 + self.n_atom # 3Fix+Header+2Button
            
            # In case of index variable arrays, create a new Frame for
            # every parameter
            par_frame = BlancFrame(self.content_frame,
                                   rows=num_rows,
                                   columns=num_columns,
                                   frame_id=curr_frame_id)
            par_frame.grid(sticky="NESW")
            self.bind_mouse_event(par_frame)
            # Add the new Frame to the list of Frames
            self.par_frame_list.append(par_frame)
            # Determine the index of the current Frame
            curr_frame_index = len(self.par_frame_list) - 1
            
            # Add the Label for the parameter
            label = self.add_label(parent=par_frame, label_text=par_name,
                                   width=INDEX_NAME_WIDTH)
            label.grid(row=row_index, column=0, sticky="NESW")
    
            # Add the Info Button for the parameter
            btn_info = self.add_button(parent=par_frame,
                                       w=INFO_WIDTH,
                                       h=INFO_HEIGHT, 
                                       tool_tip_text=short_desc)
            self.photo=tk.PhotoImage(file="info_sign_1.gif")
            btn_info.config(image=self.photo)
            btn_info.image = self.photo;
            btn_info.config(takefocus=False)
            btn_info.config(
                command=lambda: messagebox.showinfo(par_name, long_desc))
            btn_info.grid(row=row_index,column=1,sticky="W")
                    
            # Add the Entry for the parameter  
            entry = self.add_entry(parent=par_frame, par_name=par_name,
                                   entry_text="")
            entry.grid(row=row_index, column=2, sticky="NESW")

            # Get the number of elements for the current parameter
            dim = len(index_var_list)
            # Set the Header text
            header_text = '/'.join(index_var_list)
            header_text = header_text.replace("ATOM1", "Ion")
            header_text = header_text.replace("ATOM2", "Target")
            # Set the number of rows and columns of the array
            if dim == 1:
                if "ATOM1" in index_var_list or "ATOM2" in index_var_list:
                    # Create a 1 x NATOM array
                    # Fill the Header row with Labels for the ATOMS
                    label = self.add_label(parent=par_frame,
                                           label_text=header_text)
                    for i in range(self.n_atom):
                        label = self.add_label(parent=par_frame,
                                               label_text="ATOM " + str(i+1))
                    # Add a new row with a Label and Entries
                    label = self.add_label(parent=par_frame, label_text="")
                    for i in range(self.n_atom):
                        entry = self.add_entry(parent=par_frame, 
                                               par_name=par_name,
                                               entry_text="")                    
                    # Add the right arrow Button
                    button_r = self.add_button(parent=par_frame, btn_text="r",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_r, "arrow_r.gif", 'r')
                    button_r.grid(row=row_index, column=num_columns - 1)
                elif "REGION" in index_var_list and "geom" in str(par_frame):
                    # Create an NR x 1 array
                    # Fill the Header row with Labels for the REGIONS
                    label = self.add_label(parent=par_frame,
                                           label_text=header_text)
                    label = self.add_label(parent=par_frame, label_text="")                    
                    # Add new rows with a Label and Entry
                    for i in range(self.n_r):
                        label_text = "REGION " + str(i+1)
                        label = self.add_label(parent=par_frame,
                                               label_text=label_text)
                        entry = self.add_entry(parent=par_frame, 
                                               par_name=par_name,
                                               entry_text="")         
                    # Add the down arrow Button
                    button_d = self.add_button(parent=par_frame, btn_text="d",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_d, "arrow_d.gif", 'd')
                    button_d.grid(row=row_index ,column=num_columns - 1)
                elif "REGION" in index_var_list:
                    # Create a 1 x NR array
                    # Fill the Header row with Labels for the REGIONS
                    label = self.add_label(parent=par_frame,
                                           label_text=header_text)
                    for i in range(self.n_r):                        
                        label = self.add_label(parent=par_frame,
                                               label_text="REGION " + str(i+1))                    
                    # Add a new row with a Label and Entries
                    label = self.add_label(parent=par_frame, label_text="")
                    for i in range(self.n_r):
                        entry = self.add_entry(parent=par_frame, 
                                               par_name=par_name, 
                                               entry_text="")
                    # Add the right arrow Button
                    button_r = self.add_button(parent=par_frame, btn_text="r",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_r, "arrow_r.gif", 'r')
                    button_r.grid(row=row_index, column=num_columns - 1)
                elif "POINT" in index_var_list:
                    # Create a special array for POINT
                    # Fill the Header row for the POINTS
                    label = self.add_label(parent=par_frame,
                                           label_text=header_text)
                    label = self.add_label(parent=par_frame, label_text="")
                    label = self.add_label(parent=par_frame, label_text="")                    
                    # Add a new row with a Label for the Region and Entry
                    label = self.add_label(parent=par_frame, 
                                           label_text="POINT 1")
                    entry = self.add_entry(parent=par_frame, par_name=par_name,
                                           entry_text="", add_to_list=False)                    
                    label = self.add_label(parent=par_frame, label_text="")                    
                    # The first row needs 3 elements, because the
                    # algorythm takes 3 elements per row and it does
                    # not consider the '+' Button. The second row needs
                    # 3 elements because it does not have a '-' Button.
                                        
                    # Add the '+' and down arrow Buttons
                    button_add = self.add_button(parent=par_frame, btn_text="+",
                                                 w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_add, "add.gif", '+')
                    button_add.grid(row=row_index ,column=num_columns - 2)
                    button_d = self.add_button(parent=par_frame, btn_text="d",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_d, "arrow_d.gif", 'd')
                    button_d.grid(row=row_index ,column=num_columns - 1)
            elif dim == 2:
                if ("REGION" in index_var_list and 
                    ("ATOM1" in index_var_list or "ATOM2" in index_var_list)):
                    # Create an NR x NATOM array
                    # Fill the Header row for the ATOMS
                    label = self.add_label(parent=par_frame,
                                           label_text=header_text)
                    for i in range(self.n_atom):
                        label = self.add_label(parent=par_frame,
                                               label_text="ATOM " + str(i+1))                    
                    # Add new rows with a Label and Entries
                    for i in range(self.n_r):
                        label = self.add_label(parent=par_frame,
                                               label_text="REGION " + str(i+1))
                        for i in range(self.n_atom):
                            entry = self.add_entry(parent=par_frame, 
                                                   par_name=par_name,
                                                   entry_text="")         
                    # Add the two arrow Buttons
                    button_d = self.add_button(parent=par_frame, btn_text="d",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_d, "arrow_d.gif", 'd')
                    button_d.grid(row=row_index ,column=num_columns - 2)
                    
                    button_r = self.add_button(parent=par_frame, btn_text="r",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_r, "arrow_r.gif", 'r')
                    button_r.grid(row=row_index, column=num_columns - 1)
                elif "ATOM1" in index_var_list and "ATOM2" in index_var_list:
                    # Create an NATOM x NATOM array
                    # Fill the Header row for the ATOMS
                    label = self.add_label(parent=par_frame,
                                           label_text=header_text)
                    for i in range(self.n_atom):
                        label = self.add_label(parent=par_frame,
                                               label_text="ATOM " + str(i+1))                    
                    # Add new rows with a Label and Entries
                    for i in range(self.n_atom):
                        label = self.add_label(parent=par_frame,
                                               label_text="ATOM " + str(i+1))
                        for i in range(self.n_atom):
                            entry = self.add_entry(parent=par_frame, 
                                                   par_name=par_name,
                                                   entry_text="")         
                    # Add the two arrow Buttons
                    button_d = self.add_button(parent=par_frame, btn_text="d",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_d, "arrow_d.gif", 'd')
                    button_d.grid(row=row_index ,column=num_columns - 2)
                    
                    button_r = self.add_button(parent=par_frame, btn_text="r",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                    self.set_button(button_r, "arrow_r.gif", 'r')
                    button_r.grid(row=row_index, column=num_columns - 1)
                    
            # Update the Button commands
            self.update_buttons_command(curr_frame_index, index_var_list)
        # If the parameter is a boolean (Checkbutton)
        elif is_bool:
            # Set the boolean Frame as the parent frame
            par_frame = self.content_frame_bool
            
            # Add the Checkbutton for the parameter
            checkbutton = self.add_checkbutton(parent=par_frame,
                                               par_name=par_name,
                                               cb_value=default_value,
                                               default_value=default_value)
            checkbutton.grid(row=row_index,
                             column=ELEMENTS_PER_PARAM*self.params_in_row,
                             sticky="NESW")
            
            # Add the Label for the parameter
            label = self.add_label(parent=par_frame,label_text=par_name)
            label.grid(row=row_index,
                       column=1 + ELEMENTS_PER_PARAM*self.params_in_row,
                       sticky="NESW")
    
            # Add the Info Button for the parameter
            btn_info = self.add_button(parent=par_frame,
                                       w=INFO_WIDTH,
                                       h=INFO_HEIGHT, 
                                       tool_tip_text=short_desc)
            self.photo=tk.PhotoImage(file="info_sign_1.gif")
            btn_info.config(image=self.photo)
            btn_info.image = self.photo;
            btn_info.config(takefocus=False)
            btn_info.config(
                    command=lambda: messagebox.showinfo(par_name, long_desc))
            btn_info.grid(row=row_index,
                          column=2 + ELEMENTS_PER_PARAM*self.params_in_row,
                          sticky="W")            
        # If the parameter is an Entry
        else:
            # Set the entry frame as the parent frame
            par_frame = self.content_frame_entry
            
            # Add the Label for the parameter
            label = self.add_label(parent=par_frame, label_text=par_name)
            label.grid(row=row_index,
                       column=ELEMENTS_PER_PARAM*self.params_in_row,
                       sticky="NESW")
    
            # Add the Info Button for the parameter
            btn_info = self.add_button(parent=par_frame,
                                       w=INFO_WIDTH,
                                       h=INFO_HEIGHT, 
                                       tool_tip_text=short_desc)
            self.photo=tk.PhotoImage(file="info_sign_1.gif")
            btn_info.config(image=self.photo)
            btn_info.image = self.photo;
            btn_info.config(takefocus=False)
            btn_info.config(
                command=lambda: messagebox.showinfo(par_name, long_desc))
            btn_info.grid(row=row_index,
                          column=1 + ELEMENTS_PER_PARAM*self.params_in_row,
                          sticky="W")            
            
            # Add the Entry for the parameter  
            entry = self.add_entry(parent=par_frame, par_name=par_name,
                                   entry_text=default_value,
                                   default_value=default_value)
            entry.grid(row=row_index,
                       column=2 + ELEMENTS_PER_PARAM*self.params_in_row,
                       sticky="NESW")
                
    def add_parameter(self, par_name, index_var_list=None, default_value="",
                      short_desc="", long_desc="",
                      is_bool=False, is_index_var=False):
        """
        Create a new frame for the given parameter, add it to the 
        parameter frame list and add it to the scrollable frame to make
        it visible for the user.

        :param par_name: name of the parameter
        :param index_var_list: list of all index variables for this 
                               parameter
        :param default_value: default value of the parameter
        :param short_desc: short description of the parameter
        :param long_desc: long description of the parameter
        :param is_bool: true, if the parameter is a boolean
        :param is_index_var: true, if the parameter is an index 
                             variable array
        """        
        if index_var_list is None:
            index_var_list = []
        
        # Check the type of the parameter
        if is_index_var:
            # Reset the counter, since there is only 1 index variable
            # parameter per row
            self.params_in_row = 0       
            # Add the parameter to the content frame
            self.add_content_in_par_frame(
                par_name=par_name,
                index_var_list=index_var_list,
                default_value=default_value,
                short_desc=short_desc,
                long_desc=long_desc,
                is_bool=is_bool,
                row_index=0,
                is_index_var=is_index_var)
            # Increase the counter
            self.num_index += 1
        elif is_bool:
            # If the parameter is the first boolean, reset the counter
            if self.num_bools == 0:
                self.params_in_row = 0
            # Set the boolean frame as the parent frame
            par_frame = self.content_frame_bool
            self.bind_mouse_event(par_frame)
            # Add the parameter to the content frame
            self.add_content_in_par_frame(
                     par_name=par_name,
                     index_var_list=index_var_list,
                     default_value=default_value,
                     short_desc=short_desc,
                     long_desc=long_desc,
                     is_bool=is_bool,
                     row_index= self.num_bools // BOOL_PARAMS_PER_ROW,
                     is_index_var=is_index_var)
            # Increase counters
            self.num_bools += 1
            self.params_in_row += 1
            # Fold the counter at the end of the row
            self.params_in_row = self.params_in_row % BOOL_PARAMS_PER_ROW
        else:
            # If the parameter is the first entry, reset the counter
            if self.num_entries == 0:
                self.params_in_row = 0
            # Set the entry frame as the parent frame
            par_frame = self.content_frame_entry
            self.bind_mouse_event(par_frame)
            # Add the parameter to the content frame
            self.add_content_in_par_frame(
                par_name=par_name,
                index_var_list=index_var_list,
                default_value=default_value,
                short_desc=short_desc,
                long_desc=long_desc,
                is_bool=is_bool,
                row_index= self.num_entries // ENTRY_PARAMS_PER_ROW,
                is_index_var=is_index_var)
            # Increase counters
            self.num_entries += 1
            self.params_in_row += 1
            # Fold the counter at the end of the row
            self.params_in_row = self.params_in_row % ENTRY_PARAMS_PER_ROW

    def add_button(self, parent, btn_text="Button", w=3, h=3, 
                   tool_tip_text=None):
        btn = tk.Button(parent, text=btn_text, width=w, height=h)
        if tool_tip_text != None:
            balloon = Pmw.Balloon(btn)
            balloon.bind(btn, tool_tip_text)
        self.bind_mouse_event(btn)
        return btn

    def add_label(self, parent, label_text, label_text_anchor=tk.W, width=None):
        if width is None:
            label = tk.Label(parent, text=label_text, anchor=label_text_anchor)
        else:
            label = tk.Label(parent, text=label_text, 
                             anchor=label_text_anchor, width=width)
                
        self.bind_mouse_event(label)
        return label

    def add_entry(self, parent, par_name, entry_text, default_value="",
                  tool_tip_text="", disabledbackground="gray", 
                  disabledforeground="white", add_to_list=True):
        # Change the entry text and default value of NR and NATOM, to 
        # the values specified in the welcome screen, if the datatype
        # of the default value is not an int (if it is, it should be 
        # kept as its likely the value from the specified file) 
        # TODO:...
        if par_name == 'NR':
            if not isinstance(default_value, int):
                entry_text = str(self.n_r)
                default_value = self.n_r
        elif par_name == 'NATOM':
            if not isinstance(default_value, int):
                entry_text = str(self.n_atom)
                default_value = self.n_atom
        
        entry_string_var = tk.StringVar(value=entry_text)
                
        entry = tk.Entry(parent, 
                         textvariable=entry_string_var,
                         disabledbackground=disabledbackground,
                         disabledforeground=disabledforeground)
        
        # Disable the two fields in the GUI
        if par_name == 'NR' or par_name == 'NATOM':
            entry.config(state='disabled')
            
        if add_to_list:
            self.ui_data_list.add(par_name=par_name, 
                                  tk_widget=entry,
                                  widget_variable=entry_string_var,
                                  default_value=default_value)
            self.update_if_obligatory_entries()
        if tool_tip_text != "":
            balloon = Pmw.Balloon(entry)
            balloon.bind(entry, tool_tip_text)
        self.bind_mouse_event(entry)
        return entry

    def add_checkbutton(self, parent, par_name, cb_value="T",
                        default_value="", on_value="T", off_value="F"):
        cb_string_var = tk.StringVar()
        checkbutton = tk.Checkbutton(parent, text="",
                                     variable=cb_string_var,
                                     onvalue=on_value,
                                     offvalue=off_value)
        cb_string_var.set(cb_value)
        checkbutton.config(command=lambda: self.update_if_obligatory_entry(
            par_name=par_name))
        self.ui_data_list.add(par_name=par_name, tk_widget=checkbutton,
                              widget_variable=cb_string_var,
                              default_value=default_value)
        self.bind_mouse_event(checkbutton)
        return checkbutton

    def update_if_obligatory_entry(self, par_name):
        """
        Check for each tk.Entry if "obligatory if" condition is true or
        false and set the state of the tk.Entry to activate or deactivate
        the parameter.

        :par_name: Name of a bool paramter
        """
        widget_variable = self.ui_data_list.get_variable(par_name)
        obligatory_if = str(par_name + "=" + widget_variable.get())

        for ui_data in self.ui_data_list.data_list:
            if ui_data[1].winfo_class() == "Entry":
                item_name = ui_data[0]
                default_value = ui_data[3]
                if isinstance(default_value, str) and \
                    obligatory_if in default_value:
                    widgets = self.ui_data_list.get_widgets(item_name)
                    for widget in widgets:
                        widget.config(state='normal')
                elif isinstance(default_value, str) and \
                    par_name in default_value:
                    widgets = self.ui_data_list.get_widgets(item_name)
                    for widget in widgets:
                        widget.config(state='disabled')

    def update_if_obligatory_entries(self):
        """
        Update the state of a new tk.Entry.
        """
        for ui_data in self.ui_data_list.data_list:
            if ui_data[1].winfo_class() == "Checkbutton":
                # for each flag, update all entries of the parameters
                self.update_if_obligatory_entry(par_name=ui_data[0])

#    def toggle_adv(self):
#        if self.button_frame_show_adv.is_state_show_basic():
#            self.show_all()
#        else:
#            self.show_basic()
#        self.button_frame_show_adv.toggle_state()
#
#    def get_parent(self, is_basic=True):
#        if is_basic is True:
#            return self.content_frame_basic
#        else:
#            return self.content_frame_adv

    def bind_mouse_event(self, parent):
        """
        bind_mouse_event bind the mouse scrolling event with the mouse_wheel
        function, which change depending on the scrolling value the y-view
        of the main_canvas.
        """
        if parent is not None:
            # add mouse scrolling event for Darwin, Windows and Linux
            if OS == 'Windows' or OS == 'Darwin':
                # with Windows and Mac OS (OS X)
                parent.bind(sequence="<MouseWheel>", func=self.mouse_wheel)
            else:
                # with Linux
                parent.bind(sequence="<Button-4>", func=self.mouse_wheel)
                parent.bind(sequence="<Button-5>", func=self.mouse_wheel)

    def mouse_wheel(self, event):
        if OS == 'Linux':
            if event.num == 4:
                self.main_canvas.yview_scroll(int(event.delta),"units")
            elif event.num == 5:
                self.main_canvas.yview_scroll(int(-1 * event.delta),"units")
        elif OS == 'Windows':
            self.main_canvas.yview_scroll(int(-1 * event.delta/120),"units")
        elif OS == 'Darwin':
            self.main_canvas.yview_scroll(int(-1 * event.delta),"units")
