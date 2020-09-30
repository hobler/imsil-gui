"""
This module defines a tk.Frame and creates a row for each parameter 
with the following elements: 
    - a tk.Label with the parameter name, 
    - an info Button which displays the short description of the 
      parameter when hovered and pops up a window with a long 
      description when clicked
    - a tk.Entry that contains the parameter value (or a tk.Checkbutton
      if the parameter is of type boolean)
    - a tk.Entry and arrows that allow to expand the array for 
      parameters of the type index variable array

"""

import platform
import Pmw
import tkinter as tk
from tkinter import messagebox

from DataModel.DataList import DataList
from UI.Canvas.blanc.blanc_canvas import BlancCanvas
from UI.Frames.blanc.blanc_frame import BlancFrame

from UI.Frames.blanc.blanc_frame import WELCOME as WELCOME
#from UI.Frames.blanc.blanc_frame import DEFAULT as DEFAULT
from UI.Frames.blanc.blanc_frame import MAIN as MAIN
from UI.Frames.blanc.blanc_frame import BOOLEAN as BOOLEAN
from UI.Frames.blanc.blanc_frame import ENTRY as ENTRY
from UI.Frames.blanc.blanc_frame import INDEX_COLLAPSE as INDEX_COLLAPSE
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_R as INDEX_EXPAND_R
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_D as INDEX_EXPAND_D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_RD as INDEX_EXPAND_RD

OS = platform.system()


# Configure the width of the widgets
INFO_WIDTH = 10 # Info Button width
INFO_HEIGHT = 10 # Info Button height
ARROW_WIDTH = 25 # Width of arrow to expand index variable array
ARROW_HEIGHT = 25 # Height of arrow to expand index variable array

# Width of the parameter name field for index variable arrays. The use
# of a width is necessary, since every parameter has a separate frame
# and thus they can't be aligned by using weights
INDEX_NAME_WIDTH = 8

# Number of parameters per row for each type of parameter
BOOL_PARAMS_PER_ROW = 4
ENTRY_PARAMS_PER_ROW = 2
INDEX_PARAMS_PER_ROW = 1
# Number of elements (columns) per parameter. Currently three
# elements are used: name, info button, entry/checkbox
ELEMENTS_PER_PARAM = 3

# The number of elements for Index Variable Array parameters
# 1 Label & 1 Info Button (+ Entry turned on & off)
NUM_ELEMS = 2 


class ImsilScrollFrame(BlancFrame):
    """
    In the initialization only the scrollable area is created. Use 
    function add_parameter to add new parameters to the frame.
    """

    def __init__(self, parent, index_var_list=None, nr=2, natom=3, 
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Save all index variables in a list
        if index_var_list is None:
            self.index_var_list = list()
        else:
            self.index_var_list = index_var_list
            
        # Assign the number of Regions and Atoms
        self.n_r = nr.get()
        self.n_atom = natom.get()        

        # Define the number of columns for the boolean and entry 
        # parameters
        self.columns_b = BOOL_PARAMS_PER_ROW * ELEMENTS_PER_PARAM
        self.columns_e = ENTRY_PARAMS_PER_ROW * ELEMENTS_PER_PARAM
        # Define the number of columns for index variable arrays 
        # (1 Label, 1 Info, 1 Entry, 1 Column Header, 2 Buttons)
        self.columns_i = 6 + self.n_atom

        # Define the counter variable to track the number of parameters
        # in the current row
        self.params_in_row = 0
        # Initialize the counter variables for each type of parameter
        self.num_bools = 0
        self.num_entries = 0
        self.num_index = 0

        # Use a separate frame for boolean and entry type parameters
        # and a separate frame for each index variable array parameter
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

        # Create the frames for the boolean and entry type parameters
        self.content_frame_bool = BlancFrame(self.content_frame,
                                             columns=self.columns_b,
                                             frame_id=BOOLEAN)
        self.content_frame_bool.grid(sticky="NESW")
        

        self.content_frame_entry = BlancFrame(self.content_frame,
                                              columns=self.columns_e,
                                              frame_id=ENTRY)
        self.content_frame_entry.grid(sticky="NESW")
        
        # Set the frame id for index variable array type parameters
        self.index_var_frame_id = INDEX_COLLAPSE

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
        """
        self.main_canvas.itemconfig("self.content_frame", width=event.width)

    def update_scrollregion(self, event):
        """
        Is automatically called at scrolling
        """
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))


    def update_buttons_command(self, par_frame_index, par_name, index_var_list,
                               default_value, short_desc, long_desc, is_bool):
        """
        Go through each widget in the parameter frame and update the 
        parameter values of the button commands. This is necessary to
        switch the functionality assigned to the buttons, depending on
        their state.
        """
        par_frame = self.par_frame_list[par_frame_index]
        for child in par_frame.winfo_children():
            if child.winfo_class() == 'Button':
                child_grid_row = child.grid_info()['row']
                # If it is a down arrow button (marked with 'd')
                if 'd' == child.cget('text'):
                    child.config(
                        command=lambda row_index=child_grid_row:
                        self.open_index_var_d(
                            par_frame_index=par_frame_index,
                            par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc,
                            is_bool=is_bool,
                            row_index=row_index,
                            is_index_var=False
                        )
                    )
                # If it is an up arrow button (marked with 'u')
                if 'u' == child.cget('text'):
                    child.config(
                        command=lambda row_index=child_grid_row:
                        self.close_index_var_u(
                            par_frame_index=par_frame_index,
                            par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc,
                            is_bool=is_bool,
                            row_index=row_index,
                            is_index_var=False
                        )
                    ) 
                # If it is a right arrow button (marked with 'r')
                if 'r' == child.cget('text'):
                    child.config(
                        command=lambda row_index=child_grid_row:
                        self.open_index_var_r(
                            par_frame_index=par_frame_index,
                            par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc,
                            is_bool=is_bool,
                            row_index=row_index,
                            is_index_var=False
                        )
                    )
                # If it is a left arrow button (marked with 'l')
                if 'l' == child.cget('text'):
                    child.config(
                        command=lambda row_index=child_grid_row:
                        self.close_index_var_l(
                            par_frame_index=par_frame_index,
                            par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc,
                            is_bool=is_bool,
                            row_index=row_index,
                            is_index_var=False
                        )
                    )            


    def open_index_var_r(self, par_frame_index, par_name, index_var_list, 
                         default_value, short_desc, long_desc, is_bool,
                         is_index_var, row_index):
        """
        This method is used to expand the array of an index variable
        array parameter horizontally/to the right.
        """
        # Assign the corresponding frame    
        par_frame = self.par_frame_list[par_frame_index]    

        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):            
            if widget.winfo_class() == "Button" :
                # If the down Button is visible, the array is collapsed
                if 'd' == widget.cget('text'):
                    IS_DOWN = False
                # If the up Button is visible, the array is expanded
                elif 'u' == widget.cget('text'):
                    IS_DOWN = True
                # Get the right Button
                elif 'r' == widget.cget('text'):
                    right_arrow_btn = widget    

        # If the array is collapsed currently
        if not IS_DOWN:
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
                          i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1) and 
                          widget.winfo_class() == "Entry"):
                    widget.delete(0, "end")  # Delete
                    widget.insert(0, curr_val)  # Readd 
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()
                # Show the first row with the Header for the Atoms
                elif i < ((NUM_ELEMS+1) + (self.n_atom+1)):
                    widget.grid(row=0, column=i, stick="NESW")
                # Show the second row with the Label for the Region and
                # the Entries for the Atoms
                elif i < ((NUM_ELEMS+1) + 2*(self.n_atom+1)):
                    widget.grid(row=1, column=i-(self.n_atom+1), stick="NESW")
        # If the array is expanded downwards
        else:
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide all other elements (except the two arrow Buttons)
                elif i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1):
                    widget.grid_forget()
            # Iterate through every widget, and readd them
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()        
                # Show all other widgets
                elif i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (self.n_atom+1)
                    curr_col = i - curr_row*(self.n_atom+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, stick="NESW")
                                        
# TODO: change accordingly later   
#        # Create a temporary variable to fill the columns
#        tmp_column_index = 1       
#        # Add a Label and an Entry for each index variable
#        for index_var in self.index_var_list:
#            temp_column_index += 2
#            label = self.add_label(parent=par_frame,
#                                   label_text=index_var)
#            label.grid(row=row_index, column=temp_column_index,
#                       sticky="NESW")
#            entry = self.add_entry(parent=par_frame, par_name=par_name,
#                                   entry_text="")
#            entry.grid(row=row_index, column=temp_column_index + 1,
#                       sticky="NESW")
#            if index_var not in index_var_list:
#                # Disable Entry of the index variable if current
#                # parameter doesn't use it
#                entry.config(state='disabled')
                
        # Change the right arrow button to a left arrow button
        btn_l = right_arrow_btn
        self.photo_l=tk.PhotoImage(file="arrow_l.gif")
        btn_l.config(image=self.photo_l)
        btn_l.image = self.photo_l;
        btn_l.config(takefocus=False)
        btn_l.config(text="l")
        
        # Update the button commands (so the closing funcionality gets
        # assigned to the button)
        self.update_buttons_command(par_frame_index=par_frame_index,
                                    par_name=par_name,
                                    index_var_list=index_var_list,
                                    default_value=default_value,
                                    short_desc=short_desc,
                                    long_desc=long_desc,
                                    is_bool=is_bool)
        
        # If the array is expanded downwards currently
        if IS_DOWN:
            # Update the UI to match the configuration for the expanded case
            par_frame.update_grid_columnconfigure(frame_id=INDEX_EXPAND_RD)
        else:
            # Update the UI to match the configuration for the expanded case
            par_frame.update_grid_columnconfigure(frame_id=INDEX_EXPAND_R)
        
    def close_index_var_l(self, par_frame_index, par_name, index_var_list,
                          default_value, short_desc, long_desc, is_bool,
                          is_index_var, row_index):        
        """
            This method is used to collapse the array of an index variable
            array parameter horizontally/to the left.
        """
        # Assign the corresponding frame 
        par_frame = self.par_frame_list[par_frame_index]        

        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):            
            if widget.winfo_class() == "Button":
                # If the down Button is visible, the array is collapsed
                if 'd' == widget.cget('text'):
                    IS_DOWN = False
                # If the up Button is visible, the array is expanded
                elif 'u' == widget.cget('text'):
                    IS_DOWN = True
                # Get the left Button
                elif 'l' == widget.cget('text'):
                    left_arrow_btn = widget

        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info button
            if i < NUM_ELEMS:
                continue
            # Show the single Entry
            elif i == NUM_ELEMS:
                widget.grid(row=row_index, column=NUM_ELEMS, sticky="NESW")
            # Hide all other widgets
            elif i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1):
                widget.grid_forget()                  
                
        # If the array is expanded downwards readd the widgets
        if IS_DOWN:
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()
                elif (i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1) and 
                      ((i - (NUM_ELEMS+1)) % (self.n_atom+1) == 0 or 
                       (i - (NUM_ELEMS+1)) % (self.n_atom+1) == 1)):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (self.n_atom+1)
                    curr_col = i - curr_row*(self.n_atom+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, stick="NESW")
        # Otherwise check, if all Entry values are the same
        else:
            items = []
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Get the reference of the single Entry
                elif i == NUM_ELEMS:
                    curr_widget = widget                  
                # Get the value of all other Entry widgets
                elif (i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1) and 
                          widget.winfo_class() == "Entry"):
                    items.append(widget.get())  # Delete

            # If all values are the same
            if all(items[0] == item for item in items):
                curr_widget.delete(0, "end")  # Delete
                curr_widget.insert(0, items[0])  # Readd 
            else:
                curr_widget.delete(0, "end")  # Delete
                curr_widget.insert(0, "Multiple values")  # Readd 
                
            
        # Change the left arrow button to the right arrow button          
        btn_r = left_arrow_btn
        self.photo_r=tk.PhotoImage(file="arrow_r.gif")
        btn_r.config(image=self.photo_r)
        btn_r.image = self.photo_r;
        btn_r.config(takefocus=False)
        btn_r.config(text="r")
        
        # Update the button commands (so the opening funcionality gets
        # assigned to the button)
        self.update_buttons_command(par_frame_index=par_frame_index,
                            par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc,
                            is_bool=is_bool)
        
        # If the array is expanded downwards currently
        if IS_DOWN:
            # Update the UI to match the configuration for the expanded case
            par_frame.update_grid_columnconfigure(frame_id=INDEX_EXPAND_D)
        else:
            # Update the UI to match the configuration for the collapsed case
            par_frame.update_grid_columnconfigure(frame_id=INDEX_COLLAPSE)
    
    def open_index_var_d(self, par_frame_index, par_name, index_var_list, 
                         default_value, short_desc, long_desc, is_bool,
                         is_index_var, row_index):
        """
        This method is used to expand the array of an index variable
        array parameter vertically/down.
        """
        # Assign the corresponding frame    
        par_frame = self.par_frame_list[par_frame_index]

        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):            
            if widget.winfo_class() == "Button":
                # If the right Button is visible, the array is collapsed
                if 'r' == widget.cget('text'):
                    IS_RIGHT = False
                # If the left Button is visible, the array is expanded
                elif 'l' == widget.cget('text'):
                    IS_RIGHT = True
                # Get the down Button
                elif 'd' == widget.cget('text'):
                    down_arrow_btn = widget    

        # If the is collapsed currently    
        if not IS_RIGHT:
            # Iterate through every widget, and change their value, to
            # match the value of the single Entry
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Get the value of the single Entry
                elif i == NUM_ELEMS:
                    curr_val = widget.get()                    
                # Set the value of all other widgets
                elif (curr_val != "Multiple values" and 
                          i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1) and 
                          widget.winfo_class() == "Entry"):
                    widget.delete(0, "end")  # Delete
                    widget.insert(0, curr_val)  # Readd 
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()
                elif (i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1) and 
                      ((i - (NUM_ELEMS+1)) % (self.n_atom+1) == 0 or 
                       (i - (NUM_ELEMS+1)) % (self.n_atom+1) == 1)):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (self.n_atom+1)
                    curr_col = i - curr_row*(self.n_atom+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, stick="NESW")
        # If the array is expanded to the right
        else:
#            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Hide the single Entry
                elif i == NUM_ELEMS:
                    widget.grid_forget()        
                # Show all other widgets below the 2nd row (the widgets
                # in the first and second row are visible already)
                elif (i >= ((NUM_ELEMS+1) + 2*(self.n_atom+1)) and
                      i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1)):
                    # Calculate the current row and column
                    curr_row = (i - (NUM_ELEMS+1)) // (self.n_atom+1)
                    curr_col = i - curr_row*(self.n_atom+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, stick="NESW")    
                
        # Change the down arrow button to an up arrow button
        btn_u = down_arrow_btn
        self.photo_u=tk.PhotoImage(file="arrow_u.gif")
        btn_u.config(image=self.photo_u)
        btn_u.image = self.photo_u;
        btn_u.config(takefocus=False)
        btn_u.config(text="u")
        
        # Update the button commands (so the closing funcionality gets
        # assigned to the button)
        self.update_buttons_command(par_frame_index=par_frame_index,
                                    par_name=par_name,
                                    index_var_list=index_var_list,
                                    default_value=default_value,
                                    short_desc=short_desc,
                                    long_desc=long_desc,
                                    is_bool=is_bool)
        
        # If the array is expanded to the right currently
        if IS_RIGHT:
            # Update the UI to match the configuration for the expanded case
            par_frame.update_grid_columnconfigure(frame_id=INDEX_EXPAND_RD)
        else:
            # Update the UI to match the configuration for the expanded case
            par_frame.update_grid_columnconfigure(frame_id=INDEX_EXPAND_D)        

    def close_index_var_u(self, par_frame_index, par_name, index_var_list,
                          default_value, short_desc, long_desc, is_bool,
                          is_index_var, row_index):
        """
        This method is used to collapse the array of an index variable
        array parameter vertically/up.
        """
        # Assign the corresponding frame 
        par_frame = self.par_frame_list[par_frame_index]        

        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):            
            if widget.winfo_class() == "Button":
                # If the right Button is visible, the array is collapsed
                if 'r' == widget.cget('text'):
                    IS_RIGHT = False
                # If the left Button is visible, the array is collapsed
                elif 'l' == widget.cget('text'):
                    IS_RIGHT = True
                # Get the up Button
                elif 'u' == widget.cget('text'):
                    up_arrow_btn = widget

        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info button
            if i < NUM_ELEMS:
                continue
            # Show the single Entry
            elif i == NUM_ELEMS:
                widget.grid(row=row_index, column=NUM_ELEMS, sticky="NESW")
            # Hide the vertical Labels and Entries. They first pair 
            # starts after the button at i=4+2*N_ATOM. All widgets
            # afterwards are vertical widgets.
            elif i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1):
                widget.grid_forget()
            # Save the up button handle to change it
            elif widget.winfo_class() == "Button" and 'u' == widget.cget('text'):
                    up_arrow_btn = widget
                  
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
                elif i < ((NUM_ELEMS+1) + (self.n_atom+1)):
                    widget.grid(row=0, column=i, stick="NESW")
                # Show the second row with the Label for the Region and
                # the Entries for the Atoms
                elif i < ((NUM_ELEMS+1) + 2*(self.n_atom+1)):
                    widget.grid(row=1, column=i-(self.n_atom+1), stick="NESW")            
        # Otherwise check, if all Entry values are the same
        else:
            items = []
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label and info button
                if i < NUM_ELEMS:
                    continue
                # Get the reference of the single Entry
                elif i == NUM_ELEMS:
                    curr_widget = widget                  
                # Get the value of all other Entry widgets
                elif (i < (NUM_ELEMS+1) + (self.n_r+1)*(self.n_atom+1) and 
                          widget.winfo_class() == "Entry"):
                    items.append(widget.get())  # Delete

            # If all values are the same
            if all(items[0] == item for item in items):
                curr_widget.delete(0, "end")  # Delete
                curr_widget.insert(0, items[0])  # Readd 
            else:
                curr_widget.delete(0, "end")  # Delete
                curr_widget.insert(0, "Multiple values")  # Readd 
        
        
        # Change the up arrow button to the down arrow button          
        btn_d = up_arrow_btn
        self.photo_d=tk.PhotoImage(file="arrow_d.gif")
        btn_d.config(image=self.photo_d)
        btn_d.image = self.photo_d;
        btn_d.config(takefocus=False)
        btn_d.config(text="d")
        
        # Update the button commands (so the opening funcionality gets
        # assigned to the button)
        self.update_buttons_command(par_frame_index=par_frame_index,
                            par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc,
                            is_bool=is_bool)
            
        
        # If the array is expanded to the right currently
        if IS_RIGHT:
            # Update the UI to match the configuration for the expanded case
            par_frame.update_grid_columnconfigure(frame_id=INDEX_EXPAND_R)
        else:
            # Update the UI to match the configuration for the expanded case
            par_frame.update_grid_columnconfigure(frame_id=INDEX_COLLAPSE)

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
            # In case of index variable arrays, create a new Frame for
            # every parameter
            par_frame = BlancFrame(self.content_frame,
                                   rows=self.n_r,
                                   columns=self.columns_i,
                                   frame_id=self.index_var_frame_id)
            par_frame.grid(sticky="NESW")
            self.bind_mouse_event(par_frame)
            # Add the new Frame to the list of Frames
            self.par_frame_list.append(par_frame)
            # Determine the index of the current frame
            curr_frame_index = len(self.par_frame_list) - 1
            
            # Add the label for the parameter
            label = self.add_label(parent=par_frame, label_text=par_name,
                                   width=INDEX_NAME_WIDTH)
            label.grid(row=row_index, column=0, sticky="NESW")
    
            # Add the info button for the parameter
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

            # Fill the Header row for the ATOMS
            if(self.n_atom > 1):
                for i in range(self.n_atom + 1):
                    # The first Label should be empty
                    if i == 0:
                        # Add the Label
                        label = self.add_label(parent=par_frame,
                                               label_text="")
                    else:                        
                        # Add the Label
                        label = self.add_label(parent=par_frame,
                                               label_text="ATOM " + str(i))
            
            # Add a new row with a Label for the Region and Entries
            # for every Atom
            for i in range(self.n_r):
                # Add the Label
                label = self.add_label(parent=par_frame,
                                       label_text="REGION " + str(i+1))
                for i in range(self.n_atom):
                    # Add the Entry
                    entry = self.add_entry(parent=par_frame, par_name=par_name,
                                           entry_text="")                
 
            # Add the two arrow Buttons in the last two columns
            button_d = self.add_button(parent=par_frame, btn_text="d",
                                       w=ARROW_WIDTH, h=ARROW_HEIGHT)
            self.photo_d=tk.PhotoImage(file="arrow_d.gif")
            button_d.config(image=self.photo_d)
            button_d.image = self.photo_d;
            button_d.config(takefocus=False)
            button_d.grid(row=row_index ,column=self.columns_i - 2)
            
            button_r = self.add_button(parent=par_frame, btn_text="r",
                                       w=ARROW_WIDTH, h=ARROW_HEIGHT)
            self.photo_r=tk.PhotoImage(file="arrow_r.gif")
            button_r.config(image=self.photo_r)
            button_r.image = self.photo_r;
            button_r.config(takefocus=False)
            button_r.grid(row=row_index, column=self.columns_i - 1)
            
            # Update the button command for the two buttons
            self.update_buttons_command(par_frame_index=curr_frame_index,
                                        par_name=par_name,
                                        index_var_list=index_var_list,
                                        default_value=default_value,
                                        short_desc=short_desc,
                                        long_desc=long_desc, 
                                        is_bool=is_bool)        
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
            
            # Add the label for the parameter
            label = self.add_label(parent=par_frame,label_text=par_name)            
            label.grid(row=row_index,
                       column=1 + ELEMENTS_PER_PARAM*self.params_in_row,
                       sticky="NESW")
    
            # Add the info button for the parameter
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
            
            # Add the label for the parameter
            label = self.add_label(parent=par_frame, label_text=par_name)        
            label.grid(row=row_index,
                       column=ELEMENTS_PER_PARAM*self.params_in_row,
                       sticky="NESW")
    
            # Add the info button for the parameter
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
                  disabledforeground="white"):
        
        # Change the entry text and default value of NR and NATOM, to 
        # the values specified in the welcome screen, if the datatype
        # of the default value is not an int (if it is, it should be 
        # kept as its likely the value from the specified file)
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
