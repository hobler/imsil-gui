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
#from tkinter import ttk
from tkinter import messagebox
#from tkinter import Widget

from DataModel.DataList import DataList
from UI.Canvas.blanc.blanc_canvas import BlancCanvas
from UI.Frames.blanc.blanc_frame import BlancFrame

OS = platform.system()


# Configure elements width
INFO_WIDTH = 10 # Info Button width
INFO_HEIGHT = 10 # Info Button height
ARROW_WIDTH = 25 # Width of arrow to expand index variable array
ARROW_HEIGHT = 25 # Height of arrow to expand index variable array

# Width of the parameter name field for index variable arrays. The use
# of a width is necessary, since every parameter has a separate frame
# and thus they can't be aligned by using weights
INDEX_NAME_WIDTH = 8

# Set the number of parameters per row for each type 
BOOL_PARAMETERS_PER_ROW = 4
ENTRY_PARAMETERS_PER_ROW = 2
INDEX_PARAMETERS_PER_ROW = 1
# Set the number of elements (columns) per parameter. Currently three
# elements are used: name, info button, entry/checkbox
ELEMENTS_PER_PARAMETER = 3

# TODO: adjust accordingly
# These variables serve as placeholders to implement the index variable
# array editor
N_R = 3 # Number of horizontal elements
N_ATOM = 4 # Number of vertical elements


class ImsilScrollFrame(BlancFrame):
    """
    In the initialization only the scrollable area is created. Use 
    function add_parameter to add new parameters to the frame.
    """

    def __init__(self, parent, index_var_list=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Save all index variables in a list
        if index_var_list is None:
            self.index_var_list = list()
        else:
            self.index_var_list = index_var_list
            

        # Define the number of columns for the boolean and entry 
        # parameters
        self.columns_b = BOOL_PARAMETERS_PER_ROW * ELEMENTS_PER_PARAMETER
        self.columns_e = ENTRY_PARAMETERS_PER_ROW * ELEMENTS_PER_PARAMETER
        # For index variable arrays set the number of columns according
        # to the number of elements in the array (2 per element and 5
        # additional ones for the label, info, entry and expand buttons)
        self.columns_i =  2 * N_ATOM + 5

        # Define the counter variable to track the number of parameters
        # in the current row
        self.params_in_row = 0;
        # Initialize the counter variables for each type of parameter
        self.num_bools = 0
        self.num_entries = 0
        self.num_index = 0

        # Use a separate frame for the two groups of parameters and a
        # separate frame for each index variable array parameter
        self.par_frame_list = []
        self.ui_data_list = DataList()

        # Build the scrolling area
        self.main_canvas = BlancCanvas(self,columns=1,width=890)
        self.content_frame = BlancFrame(self.main_canvas,frame_id=0)
        # @create_window: parameter 'tags' is later required to change 
        # the window size
        self.main_canvas.create_window(0,0,
                                       window=self.content_frame,
                                       tags="self.content_frame", 
                                       anchor="nw")
        self.vertical_scrollbar = tk.Scrollbar(self,orient=tk.VERTICAL)
        self.vertical_scrollbar.grid(row=0,column=1,sticky="NES")
        self.vertical_scrollbar.config(command=self.main_canvas.yview)
        self.main_canvas.config(yscrollcommand=self.vertical_scrollbar.set)
        self.bind_mouse_event(self.content_frame)

        # Create the frames for the boolean and entry type parameters
        self.content_frame_bool = BlancFrame(self.content_frame,
                                             columns=self.columns_b,
                                             frame_id=1)
        self.content_frame_bool.grid(sticky="NESW")
        

        self.content_frame_entry = BlancFrame(self.content_frame,
                                              columns=self.columns_e,
                                              frame_id=2)
        self.content_frame_entry.grid(sticky="NESW")
        
        # Set the frame index for index variable array type parameters
        self.index_var_frame_id = 3
#        self.content_frame_index = BlancFrame(self.content_frame, columns = self.columns_i, frame_index=3)
#        self.content_frame_index.grid(sticky="NESW")        

        # Add the two frames to the list of frames
        self.par_frame_list.append(self.content_frame_bool)
        self.par_frame_list.append(self.content_frame_entry)
#        self.par_frame_list.append(self.content_frame_index)

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


    def update_buttons_command(self,par_frame_index,par_name,index_var_list,
                               default_value,short_desc,long_desc,is_bool):
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
                if 'd' in child.cget('text'):
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
                if 'u' in child.cget('text'):
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
                if 'r' in child.cget('text'):
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
                if 'l' in child.cget('text'):
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

    """
        This method is used to expand the array of an index variable
        array parameter horizontally/to the right.
    """
    def open_index_var_r(self,par_frame_index,par_name,index_var_list, 
                         default_value,short_desc,long_desc,is_bool,
                         is_index_var,row_index):
        # Assign the corresponding frame    
        par_frame = self.par_frame_list[par_frame_index]

        # Iterate through all widgets (in the order they have been 
        # added before)
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info button
            if i<2:
                continue
            # Hide the single Entry
            elif i==2:
                widget.grid_forget()
            # Show all other horizontal widgets (the first pair starts 
            # at i=2+1 and the last pair ends at 2 + 2*N_ATOM)
            elif i<(3+2*N_ATOM):
                widget.grid(row=0,column=i,stick="NESW")
            # Save the right button handle to change it
            elif widget.winfo_class()=="Button" and 'r' in widget.cget('text'):
                    right_arrow_btn = widget
            # Disable the down button
            elif widget.winfo_class()=="Button" and 'd' in widget.cget('text'):
                    widget.config(state='disabled')
                                         
# TODO: change accordingl later   
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
        
        # Update the UI to match the configuration for the expanded case
        par_frame.update_grid_columnconfigure(frame_id=4)
        
    """
        This method is used to collapse the array of an index variable
        array parameter horizontally/to the left.
    """
    def close_index_var_l(self,par_frame_index,par_name,index_var_list,
                          default_value, short_desc,long_desc, is_bool,
                          is_index_var,row_index):        
        # Assign the corresponding frame 
        par_frame = self.par_frame_list[par_frame_index]        

        # Iterate through all widgets (in the order they have been 
        # added before)
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info button
            if i<2:
                continue
            # Show the single Entry
            elif i==2:
                widget.grid(row=row_index,column=2,sticky="NESW")
            # Hide all other horizontal widgets (the first pair starts 
            # at i=2+1 and the last pair ends at i=2+2*N_ATOM)
            elif i<(3+2*N_ATOM):
                widget.grid_forget()
            # Save the left button handle to change it
            elif widget.winfo_class()=="Button" and 'l' in widget.cget('text'):
                    left_arrow_btn = widget
            # Enable the down button
            elif widget.winfo_class()=="Button" and 'd' in widget.cget('text'):
                    widget.config(state='active')                    
                
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
        
        # Update the UI to match the configuration for the collapsed case
        par_frame.update_grid_columnconfigure(frame_id=3)


    """
        This method is used to expand the array of an index variable
        array parameter vertically/down.
    """
    def open_index_var_d(self,par_frame_index,par_name,index_var_list, 
                         default_value,short_desc,long_desc,is_bool,
                         is_index_var,row_index):
        # Assign the corresponding frame    
        par_frame = self.par_frame_list[par_frame_index]

        # Initialize counter variable
        tmp_index = 0        
        # Iterate through all widgets (in the order they have been 
        # added before)
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info button
            if i<2:
                continue
            # Hide the single Entry
            elif i==2:
                widget.grid_forget()
            # Save the down button handle to change it
            elif widget.winfo_class()=="Button" and 'd' in widget.cget('text'):
                    down_arrow_btn = widget
            # Disable the right button
            elif widget.winfo_class()=="Button" and 'r' in widget.cget('text'):
                    widget.config(state='disabled')
            # Show the vertical Labels and Entries. They first pair 
            # starts after the button at i=4+2*N_ATOM. All widgets
            # afterwards are vertical widgets.
            elif i>(4+2*N_ATOM):
                # Place the Labels in the 3rd column
                if widget.winfo_class()=="Label":
                    widget.grid(row=tmp_index,column=3,stick="NESW")
                # Place the Entries in the 4th column
                if widget.winfo_class()=="Entry":
                    widget.grid(row=tmp_index,column=4,stick="NESW")
                    tmp_index += 1 # Increase the row number       
                
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
        
        # Update the UI to match the configuration for the expanded case
        par_frame.update_grid_rowconfigure(frame_id=5)
        
    """
        This method is used to collapse the array of an index variable
        array parameter vertically/up.
    """
    def close_index_var_u(self,par_frame_index,par_name,index_var_list,
                          default_value, short_desc,long_desc, is_bool,
                          is_index_var,row_index):        
        # Assign the corresponding frame 
        par_frame = self.par_frame_list[par_frame_index]        

        # Iterate through all widgets (in the order they have been 
        # added before)
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info button
            if i<2:
                continue
            # Show the single Entry
            elif i==2:
                widget.grid(row=row_index,column=2,sticky="NESW")
            # Hide the vertical Labels and Entries. They first pair 
            # starts after the button at i=4+2*N_ATOM. All widgets
            # afterwards are vertical widgets.
            elif i>(4+2*N_ATOM):
                widget.grid_forget()
            # Save the up button handle to change it
            elif widget.winfo_class()=="Button" and 'u' in widget.cget('text'):
                    up_arrow_btn = widget
            # Enable the right button
            elif widget.winfo_class()=="Button" and 'r' in widget.cget('text'):
                    widget.config(state='active')                    
                
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
        
        # Update the UI to match the configuration for the collapsed case
        par_frame.update_grid_columnconfigure(frame_id=3)


    def add_content_in_par_frame(self,par_name,index_var_list,default_value,
                                 short_desc,long_desc,is_bool,is_index_var,
                                 row_index):        
        
        """
        Take the parameter frame from the parameter frame list at the index
        par_frame_index and fill a new row with the index row_index with tk
        widgets as described in the module docstring. If there are already
        widgets in this row, all elements in the rows with index >=
        row_index have to be moved down one row to make place for the new
        row.

        :par_frame_index: parameter frame index
        :par_name: parameter name
        :index_var_list: a list of index variables that are used by this
                         parameter
        :default_value: default value of the parameter
        :short_desc: short description of the parameter
        :long_desc: long description of the parameter
        :is_bool: true, if the parameter is of type bool, false else
        :row_index: row number where the new parameter should be placed
        """  

        # Check the type of the parameter               
        if is_index_var:    
            # In case of index variable arrays, create a new frame for
            # every parameter
            par_frame = BlancFrame(self.content_frame,
                                   rows=N_R,
                                   columns=self.columns_i,
                                   frame_id=self.index_var_frame_id)
            par_frame.grid(sticky="NESW")
            self.bind_mouse_event(par_frame)
            # Add the new frame to the list of frames
            self.par_frame_list.append(par_frame)
            # Determine the index of the current frame in the list of
            # frames
            curr_frame_index = len(self.par_frame_list)-1
            
            # Add the label for the parameter
            label = self.add_label(parent=par_frame,label_text=par_name,
                                   width=INDEX_NAME_WIDTH)
            label.grid(row=row_index,column=0, sticky="NESW")
    
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
            entry = self.add_entry(parent=par_frame,par_name=par_name,
                                   entry_text="")
            entry.grid(row=row_index,column=2,sticky="NESW")

            # Add additional (horizontal) labels and entries. They are
            # added to the frame but not placed within the grid. They
            # get placed, when the user expands the array.
            for i in range(N_ATOM):
                # Add the Label
                label = self.add_label(parent=par_frame,
                                       label_text="ATOM " + str(i+1))
                # Add the Entry
                entry = self.add_entry(parent=par_frame,par_name=par_name,
                                       entry_text="")

            # Add two arrow Buttons in the last two columns, used to 
            # expand the array
            button_d = self.add_button(parent=par_frame,btn_text="d",
                                       w=ARROW_WIDTH,h=ARROW_HEIGHT)
            self.photo_d=tk.PhotoImage(file="arrow_d.gif")
            button_d.config(image=self.photo_d)
            button_d.image = self.photo_d;
            button_d.config(takefocus=False)
            button_d.grid(row=row_index,column=self.columns_i - 2)
            
            button_r = self.add_button(parent=par_frame,btn_text="r",
                                       w=ARROW_WIDTH,h=ARROW_HEIGHT)
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
            
            # Add additional (vertical) labels and entries. They are
            # added to the frame but not placed within the grid. They
            # get placed, when the user expands the array.
            for i in range(N_R):
                # Add the Label
                label = self.add_label(parent=par_frame,
                                       label_text="REGION " + str(i+1))
                # Add the Entry
                entry = self.add_entry(parent=par_frame,par_name=par_name,
                                       entry_text="")
        # If the parameter is a boolean (Checkbutton)
        elif is_bool:
            # Set the boolean frame as the parent frame
            par_frame = self.content_frame_bool
            
            # Add the Checkbutton for the parameter            
            checkbutton = self.add_checkbutton(parent=par_frame,
                                               par_name=par_name,
                                               cb_value=default_value,
                                               default_value=default_value)
            checkbutton.grid(row=row_index,
                             column=ELEMENTS_PER_PARAMETER*self.params_in_row,
                             sticky="NESW")
            
            # Add the label for the parameter
            label = self.add_label(parent=par_frame,label_text=par_name)            
            label.grid(row=row_index,
                       column=1+ELEMENTS_PER_PARAMETER*self.params_in_row,
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
                    command=lambda: messagebox.showinfo(par_name,long_desc))
            btn_info.grid(row=row_index,
                          column=2+ELEMENTS_PER_PARAMETER*self.params_in_row,
                          sticky="W")            
        # If the parameter is an Entry
        else:
            # Set the entry frame as the parent frame
            par_frame = self.content_frame_entry
            
            # Add the label for the parameter
            label = self.add_label(parent=par_frame,label_text=par_name)        
            label.grid(row=row_index,
                       column=ELEMENTS_PER_PARAMETER*self.params_in_row,
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
                          column=1+ELEMENTS_PER_PARAMETER*self.params_in_row,
                          sticky="W")            
            
            # Add the Entry for the parameter  
            entry = self.add_entry(parent=par_frame,par_name=par_name,
                                   entry_text=default_value,
                                   default_value=default_value)
            entry.grid(row=row_index,
                       column=2+ELEMENTS_PER_PARAMETER*self.params_in_row,
                       sticky="NESW")
                

    def add_parameter(self,par_name,index_var_list=None,default_value="",
                      short_desc="",long_desc="",
                      is_bool=False,is_index_var=False):
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
                row_index= 0,#self.num_index//INDEX_PARAMETERS_PER_ROW,
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
                     row_index= self.num_bools//BOOL_PARAMETERS_PER_ROW,
                     is_index_var=is_index_var)
            # Increase counters
            self.num_bools += 1
            self.params_in_row += 1
            # Fold the counter at the end of the row
            self.params_in_row = self.params_in_row%BOOL_PARAMETERS_PER_ROW          
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
                row_index= self.num_entries//ENTRY_PARAMETERS_PER_ROW,
                is_index_var=is_index_var)
            # Increase counters
            self.num_entries += 1
            self.params_in_row += 1
            # Fold the counter at the end of the row
            self.params_in_row = self.params_in_row%ENTRY_PARAMETERS_PER_ROW
                            
                

    def add_button(self,parent,btn_text="Button",w=3,h=3,tool_tip_text=None):
        btn = tk.Button(parent,text=btn_text,width=w,height=h)
        if tool_tip_text != None:
            balloon = Pmw.Balloon(btn)
            balloon.bind(btn, tool_tip_text)
        self.bind_mouse_event(btn)
        return btn

    def add_label(self,parent,label_text,label_text_anchor=tk.W,width=None):
        if width is None:
            label = tk.Label(parent,text=label_text,
                         anchor=label_text_anchor)
        else:
            label = tk.Label(parent,text=label_text,
                         anchor=label_text_anchor,width=width)
                
        self.bind_mouse_event(label)
        return label

    def add_entry(self,parent,par_name,entry_text,
                  default_value="",tool_tip_text="",
                  disabledbackground="gray",disabledforeground="white"):
        entry_string_var = tk.StringVar(value=entry_text)
        entry = tk.Entry(parent,textvariable=entry_string_var,
                         disabledbackground=disabledbackground,
                         disabledforeground=disabledforeground)
        self.ui_data_list.add(par_name=par_name,tk_widget=entry,
                              widget_variable=entry_string_var,
                              default_value=default_value)
        self.update_if_obligatory_entries()
        if tool_tip_text != "":
            balloon = Pmw.Balloon(entry)
            balloon.bind(entry, tool_tip_text)
        self.bind_mouse_event(entry)
        return entry

    def add_checkbutton(self, parent,par_name, 
                        cb_value="T",
                        default_value="",
                        on_value="T",off_value="F"):
        cb_string_var = tk.StringVar()
        checkbutton = tk.Checkbutton(parent,text="",
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
                if obligatory_if in default_value:
                    widgets = self.ui_data_list.get_widgets(item_name)
                    for widget in widgets:
                        widget.config(state='normal')
                elif par_name in default_value:
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
