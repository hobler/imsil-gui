import tkinter as tk
from tkinter import messagebox

from UI.Frames.blanc.blanc_frame import BlancFrame
from UI.Frames.blanc.blanc_frame import INDEX_COLLAPSE_1D as INDEX_COLLAPSE_1D
from UI.Frames.blanc.blanc_frame import INDEX_COLLAPSE_2D as INDEX_COLLAPSE_2D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_R_1D as INDEX_EXPAND_R_1D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_R_2D as INDEX_EXPAND_R_2D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_D_1D as INDEX_EXPAND_D_1D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_D_2D as INDEX_EXPAND_D_2D
from UI.Frames.blanc.blanc_frame import INDEX_EXPAND_RD as INDEX_EXPAND_RD

# Configure the width and height of the widgets
INFO_WIDTH = 10 # info Button width
INFO_HEIGHT = 10 # info Button height
ARROW_WIDTH = 20 # Width of the arrow (and '+'/'-') Button(s)
ARROW_HEIGHT = 20 # Height of the arrow (and '+'/'-') Button(s)

# Width of the parameter name field for index variable arrays. The use
# of a width is necessary, since every parameter has a separate frame
# and thus they can't be aligned by only using weights
INDEX_NAME_WIDTH = 8
INDEX_LABEL_WIDTH_1D = 8
INDEX_LABEL_WIDTH_2D = 12

# The number of fixed elements for index variable array parameters:
# 1 Label & 1 info Button (+ Entry turned on & off)
NUM_ELEMS = 2 


class IndexVariableArrayFrame(BlancFrame):
    """
    This is the class for the IndexVariableArrayFrame 
    
    The IndexVariableArrayFrame is a BlancFrame holding all information
    of the corresponding index variable array. Its layout is built 
    dynamically, based on the index variable it holds. Furthermore, the
    class implements all methods for collapsing/expanding the index 
    variable arrays and adding/deleting Points for the index variable
    array POINTS.
    """
    def __init__(self, parent, par_name, index_var_list, default_value,
                 short_desc, long_desc, row_index, nr=3, natom=2, 
                 *args, **kwargs):
        """
        In the initialization of the IndexVariableArrayFrame all object 
        parameters are defined, the layout is determined dynamically
        and the Buttons for expanding the array are set up.

        :param parent: the ImsilScrollFrame which holds this Frame. It 
                       is used to access the methods to add Labels,
                       Entries, etc. (this is not the parent tk widget!
                       The parent Frame is parent.content_frame)
        :param par_name: the name of the parameter
        :param index_var_list: a list of all index variables for this 
                               parameter
        :param default_value: the default value of the parameter
        :param short_desc: the short description of the parameter
        :param long_desc: the long description of the parameter
        :param row_index: the row number where the parameter should
                          be placed        
        :param nr: the number of regions for index variable arrays
        :param natom: the number of atoms for index variable arrays
        :param args: is forwarded to the super().__init__() function
        :param kwargs: is forwarded to the super().__init__() function
        """        
        self.n_r = nr
        self.n_atom = natom
        self.parent = parent  
        # The number of POINTS (only used for the POINTS index variable
        # array in the geom tab)
        self.num_points = 1
        # An Array to save the values of the index variable array. This
        # is used to keep track of the values regardless of the current
        # state of the array
        self.values=[]
        
        # Get the number of elements for the current parameter
        dim = len(index_var_list)
        # Set the number of rows and columns of the array
        if dim == 1:
            curr_frame_id = INDEX_COLLAPSE_1D
            if "ATOM1" in index_var_list or "ATOM2" in index_var_list:
                # Create a 1 x NATOM array
                self.num_rows = 2  # Header+Value
                self.num_columns = 5 + self.n_atom  # 3Fix+Header+Button
            elif ("REGION" in index_var_list and 
                  "geom" in str(parent.content_frame)):
                # Create an NR x 1 array
                self.num_rows = 2 + self.n_r  # Header+REGION0+nr rows
                self.num_columns = 5 + 1  # 3Fix+Header+Column+Button
            elif "REGION" in index_var_list:
                # Create a 1 x NR array
                self.num_rows = 2  # Header+Value
                self.num_columns = 5 + self.n_r  # 3Fix+Header+Button
            elif "POINT" in index_var_list:
                curr_frame_id = INDEX_COLLAPSE_2D
                # Create a special array for POINT (num_points x 2)
                self.num_rows = 2  # Header+Value
                self.num_columns = 6 + 1  # 3Fix+Header+Column+2Button
        elif dim == 2:
            curr_frame_id = INDEX_COLLAPSE_2D
            if ("REGION" in index_var_list and 
                ("ATOM1" in index_var_list or "ATOM2" in index_var_list)):
                # Create an NR x NATOM array
                self.num_rows = 1 + self.n_r  # Header+nr rows
                self.num_columns = 6 + self.n_atom # 3Fix+Header+2Button
            elif "ATOM1" in index_var_list and "ATOM2" in index_var_list:
                # Create an NATOM x NATOM array
                self.num_rows = 1 + self.n_atom  # Header+natom rows
                self.num_columns = 6 + self.n_atom # 3Fix+Header+2Button
        
        # Call the init of BlancFrame with the correct rows and columns
        super().__init__(parent.content_frame, self.num_rows, self.num_columns, 
                         curr_frame_id, *args, **kwargs)    

        # Add the Label for the parameter
        label = self.parent.add_label(parent=self, label_text=par_name,
                                      width=INDEX_NAME_WIDTH)
        label.grid(row=row_index, column=0, sticky="NESW")

        # Add the info Button for the parameter
        btn_info = self.parent.add_button(parent=self,
                                          w=INFO_WIDTH,
                                          h=INFO_HEIGHT, 
                                          tool_tip_text=short_desc)
        self.photo=tk.PhotoImage(file="info_sign_1.gif")
        btn_info.config(image=self.photo)
        btn_info.image = self.photo;
        btn_info.config(takefocus=False)
        btn_info.config(
                command=lambda: messagebox.showinfo(par_name, long_desc))
        btn_info.grid(row=row_index, column=1, sticky="W")
                
        # Add the Entry for the parameter  
        entry = self.parent.add_entry(parent=self, par_name=par_name,
                                      entry_text="")
        entry.grid(row=row_index, column=2, sticky="NESW")

        # Set the Header text
        header_text = '\\'.join(index_var_list)
        # Replace the texts according to the specification
        header_text = header_text.replace("REGION", "Region")
        header_text = header_text.replace("ATOM1", "Ion")
        header_text = header_text.replace("ATOM2", "Target")
        # Set the number of rows and columns of the array
        if dim == 1:
            if "ATOM1" in index_var_list or "ATOM2" in index_var_list:
                # Create a 1 x NATOM array
                # Fill the Header row with Labels for the ATOMS
                label = self.parent.add_label(parent=self,
                                              label_text=header_text,
                                              width=INDEX_LABEL_WIDTH_1D)
                for i in range(self.n_atom):
                    label = self.parent.add_label(parent=self,
                                                  label_text="ATOM "+str(i+1))
                # Add a new row with a Label and Entries
                label = self.parent.add_label(parent=self, label_text="")
                for i in range(self.n_atom):
                    entry = self.parent.add_entry(parent=self, 
                                                  par_name=par_name,
                                                  entry_text="")
                # Add the right arrow Button
                btn_r = self.parent.add_button(parent=self, btn_text="r",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_r, "arrow_r.gif", 'r')
                btn_r.grid(row=row_index, column=self.num_columns - 1)
            elif "REGION" in index_var_list and "geom" in str(self):
                # Create an NR x 1 array
                # Fill the Header row with Labels for the REGIONS
                label = self.parent.add_label(parent=self,
                                              label_text=header_text,
                                              width=INDEX_LABEL_WIDTH_1D)
                label = self.parent.add_label(parent=self, label_text="")
                # Add new rows with a Label and Entry
                # Add an extra row REGION 0
                for i in range(self.n_r+1):
                    label_text = "REGION " + str(i)
                    label = self.parent.add_label(parent=self,
                                                  label_text=label_text)
                    entry = self.parent.add_entry(parent=self, 
                                                  par_name=par_name,
                                                  entry_text="")         
                # Add the down arrow Button
                btn_d = self.parent.add_button(parent=self, btn_text="d",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_d, "arrow_d.gif", 'd')
                btn_d.grid(row=row_index ,column=self.num_columns - 1)
            elif "REGION" in index_var_list:
                # Create a 1 x NR array
                # Fill the Header row with Labels for the REGIONS
                label = self.parent.add_label(parent=self,
                                              label_text=header_text,
                                              width=INDEX_LABEL_WIDTH_1D)
                for i in range(self.n_r):                        
                    label = self.parent.add_label(parent=self,
                                                  label_text="REGION "+str(i+1))
                # Add a new row with a Label and Entries
                label = self.parent.add_label(parent=self, label_text="")
                for i in range(self.n_r):
                    entry = self.parent.add_entry(parent=self, 
                                                  par_name=par_name, 
                                                  entry_text="")
                # Add the right arrow Button
                btn_r = self.parent.add_button(parent=self, btn_text="r",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_r, "arrow_r.gif", 'r')
                btn_r.grid(row=row_index, column=self.num_columns - 1)
            elif "POINT" in index_var_list:
                # Create a special array for POINT
                # Fill the Header row with Labels for POINTS
                label = self.parent.add_label(parent=self,
                                              label_text=header_text,
                                              width=INDEX_LABEL_WIDTH_1D)
                label = self.parent.add_label(parent=self, label_text="")
                label = self.parent.add_label(parent=self, label_text="")
                # Add a new row with a Label and an Entry
                label = self.parent.add_label(parent=self, label_text="POINT 1")
                entry = self.parent.add_entry(parent=self, par_name=par_name,
                                              entry_text="", add_to_list=False)
                label = self.parent.add_label(parent=self, label_text="")
                # The first row needs 3 elements, because the
                # algorythm takes 3 elements per row and it does
                # not consider the '+' Button. The second row needs
                # 3 elements because it does not have a '-' Button.
                                    
                # Add the '+' and down arrow Buttons
                btn_add = self.parent.add_button(parent=self, btn_text="+",
                                                 w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_add, "add.gif", '+')
                btn_add.grid(row=row_index ,column=self.num_columns - 2)
                btn_d = self.parent.add_button(parent=self, btn_text="d",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_d, "arrow_d.gif", 'd')
                btn_d.grid(row=row_index ,column=self.num_columns - 1)
        elif dim == 2:
            if ("REGION" in index_var_list and 
                ("ATOM1" in index_var_list or "ATOM2" in index_var_list)):
                # Create an NR x NATOM array
                # Fill the Header row with Labels for the ATOMS
                label = self.parent.add_label(parent=self,
                                              label_text=header_text,
                                              width=INDEX_LABEL_WIDTH_2D)
                for i in range(self.n_atom):
                    label = self.parent.add_label(parent=self,
                                                  label_text="ATOM "+str(i+1))
                # Add new rows with a Label and Entries
                for i in range(self.n_r):
                    label = self.parent.add_label(parent=self,
                                                  label_text="REGION "+str(i+1))
                    for i in range(self.n_atom):
                        entry = self.parent.add_entry(parent=self, 
                                                      par_name=par_name,
                                                      entry_text="")         
                # Add the two arrow Buttons
                btn_d = self.parent.add_button(parent=self, btn_text="d",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_d, "arrow_d.gif", 'd')
                btn_d.grid(row=row_index ,column=self.num_columns - 2)
                
                btn_r = self.parent.add_button(parent=self, btn_text="r",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_r, "arrow_r.gif", 'r')
                btn_r.grid(row=row_index, column=self.num_columns - 1)
            elif "ATOM1" in index_var_list and "ATOM2" in index_var_list:
                # Create an NATOM x NATOM array
                # Fill the Header row for with Labels the ATOMS
                label = self.parent.add_label(parent=self,
                                              label_text=header_text,
                                              width=INDEX_LABEL_WIDTH_2D)
                for i in range(self.n_atom):
                    label = self.parent.add_label(parent=self,
                                                  label_text="ATOM "+str(i+1))
                # Add new rows with a Label and Entries
                for i in range(self.n_atom):
                    label = self.parent.add_label(parent=self,
                                                  label_text="ATOM "+str(i+1))
                    for i in range(self.n_atom):
                        entry = self.parent.add_entry(parent=self, 
                                                      par_name=par_name,
                                                      entry_text="")         
                # Add the two arrow Buttons
                btn_d = self.parent.add_button(parent=self, btn_text="d",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_d, "arrow_d.gif", 'd')
                btn_d.grid(row=row_index ,column=self.num_columns - 2)
                
                btn_r = self.parent.add_button(parent=self, btn_text="r",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
                self.set_button(btn_r, "arrow_r.gif", 'r')
                btn_r.grid(row=row_index, column=self.num_columns - 1)
                
        # Update the Button commands
        self.update_buttons_command(index_var_list)

    def set_button(self, widget, file, text):
        """
        Set up the Button with the specified text and picture.
                
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

    def update_buttons_command(self, index_var_list):
        """
        Update the commands assigned to the different buttons.
        
        Go through each widget in the IndexVariableArrayFrame and update
        the commands assigned to the Buttons, based on their text. 
        
        :param index_var_list: the list of all index variables for this 
                               parameter
        """
        # Iterate through every widget in the IndexVariableArrayFrame
        for child in self.winfo_children():
            if child.winfo_class() == 'Button':
                # If the Button is not placed within the grid yet, do
                # not handle it
                if not child.grid_info():
                    continue
                child_grid_row = child.grid_info()['row']
                
                # If it is a down arrow Button (marked with 'd')
                if 'd' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.open_index_var_d(index_var_list=index_var_list,
                                              row_index=row_index))
                # If it is an up arrow Button (marked with 'u')
                if 'u' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.close_index_var_u(index_var_list=index_var_list,
                                               row_index=row_index))
                # If it is a right arrow Button (marked with 'r')
                if 'r' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.open_index_var_r(index_var_list=index_var_list,
                                              row_index=row_index))
                # If it is a left arrow Button (marked with 'l')
                if 'l' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.close_index_var_l(index_var_list=index_var_list,
                                               row_index=row_index))
                # If it is a + Button (marked with '+')
                if '+' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.add_row(index_var_list=index_var_list,
                                     row_index=row_index)) 
                # If it is a - Button (marked with '-')
                if '-' == child.cget('text'):
                    child.config(command=lambda row_index=child_grid_row:
                        self.delete_row(index_var_list=index_var_list,
                                        row_index=row_index)) 
                        
    def open_index_var_r(self, index_var_list, row_index):
        """
        This method is used to expand the array of an index variable
        array parameter horizontally/to the right.
        
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Get the Button reference and array state
        right_arrow_btn, IS_DOWN, IS_RIGHT = self.get_state('r')
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(index_var_list)

        # If the array is collapsed currently
        if not IS_DOWN:
            # Set the Entry values to match the single Entry
            init =self.set_entry_values(self)
            # Save the Entry values to the array
            self.save_entry_values(self, m, n, init, IS_POINT)
            # Iterate through every widget and place them
            for i,widget in enumerate(self.children.values()):
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
                    
            # Iterate through every widget and update the values
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, info Button and the single Entry
                if i <= NUM_ELEMS:
                    continue
                # Get the Label of which the text needs to be swapped
                elif (widget.winfo_class() == "Label" and 
                      dim == 2 and
                      widget.grid_info() and
                      widget.grid_info()['row'] == 1 and 
                      widget.grid_info()['column'] == 3):
                    # Get all Label texts
                    label_text = widget.cget('text')
                    # Swap the element accordingly
                    if label_text == "REGION 1":
                        widget['text'] = "ALL REGIONS"
                    if label_text == "ATOM 1":
                        widget['text'] = "ALL ATOMS"                        
                elif widget.winfo_class() == "Entry" and widget.grid_info():
                    # Current column in the grid
                    curr_col = widget.grid_info()['column']
                    # Column in the array
                    col = curr_col - (NUM_ELEMS+2)
                    # Array with all elements from the current column
                    items = [x[col] for x in self.values]                    
                    # If all items are the same, set the first Entry
                    if all(items[0] == item for item in items):
                        widget.delete(0, "end")  # Delete
                        widget.insert(0, items[0])  # Readd
                    # Otherwise set the first Entry to "Multiple values"
                    else:
                        widget.delete(0, "end")  # Delete
                        widget.insert(0, "Multiple values")  # Readd
        # If the array is expanded downwards
        else:
            # Iterate through every (already placed) widget
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, info Button and the single Entry
                if i <= NUM_ELEMS:
                    continue
                # Get the Label of which the text needs to be swapped
                elif (widget.winfo_class() == "Label" and 
                      dim == 2 and
                      widget.grid_info() and
                      widget.grid_info()['row'] == 0 and 
                      widget.grid_info()['column'] == 4):
                    # Get all Label texts
                    label_text = widget.cget('text')
                    # Swap the elements back  accordingly
                    if label_text == "ALL REGIONS":
                        widget['text'] = "REGION 1"
                    if label_text == "ALL ATOMS":
                        widget['text'] = "ATOM 1"
                elif widget.winfo_class() == "Entry" and widget.grid_info():
                    # Current row and column in the grid
                    curr_row = widget.grid_info()['row']
                    curr_col = widget.grid_info()['column']
                    # Row and column in the array
                    row = curr_row - 1
                    col = curr_col - (NUM_ELEMS+2)
                    # Current widget value
                    curr_value = widget.get()
                    # If the value of the first Entry was "Multiple 
                    # values", replace it with the value when expanding
                    if curr_value == "Multiple values":
                        widget.delete(0, "end")  # Delete
                        widget.insert(0, self.values[row][col])  # Readd
                    # Otherwise set all values in the current row, to
                    # match the value of the first Entry
                    else:
                        for j in range(len(self.values[row])):
                            self.values[row][j] = curr_value
            # Hide every widget except the main Label and info Button
            self.hide_widgets(self, m, n)
            # Iterate through every widget, and readd them
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, the info Button and the Entry
                if i <= NUM_ELEMS:
                    continue
                # Show all other widgets
                elif i < (NUM_ELEMS+1) + (m+1)*(n+1):
                    # Calculate the current row and column in the grid
                    curr_row = (i - (NUM_ELEMS+1)) // (n+1)
                    curr_col = i - curr_row*(n+1)
                    # Place the widget
                    widget.grid(row=curr_row, column=curr_col, sticky="NESW")
                    
                    if widget.winfo_class() == "Entry" and widget.grid_info():
                        # Row and column in the array
                        row = curr_row - 1
                        col = curr_col - (NUM_ELEMS+2)
                        # Current widget value
                        curr_value = widget.get()
                        # If the current widget value is not up to date
                        if curr_value != self.values[row][col]:
                            widget.delete(0, "end")  # Delete
                            widget.insert(0, self.values[row][col])  # Readd
                
        # Change the right arrow button to a left arrow button
        self.set_button(right_arrow_btn, "arrow_l.gif", "l")
        # Update the Button commands
        self.update_buttons_command(index_var_list)
        # Set the weigths for the new state
        self.set_weights(self, dim, IS_DOWN, True, IS_POINT)
        
    def close_index_var_l(self, index_var_list, row_index):
        """
        This method is used to collapse the array of an index variable
        array parameter horizontally/to the left.
                
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Get the Button reference and array state
        left_arrow_btn, IS_DOWN, IS_RIGHT = self.get_state('l')
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(index_var_list)

        # If the array is expanded downwards readd the widgets
        if IS_DOWN:
            # Save the current values of the index variable array
            self.save_entry_values(self, m, n, False, IS_POINT)
            # Hide every widget except the main Label and info Button
            # and show the Entry
            self.hide_widgets(self, m, n, True, row_index)
            # Iterate through every widget
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, the info Button and the Entry
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
                    
                    # Because of the if condition above, only the first
                    # Entries from each row are checked
                    if widget.winfo_class() == "Entry":
                        # Get the values of the according row (row num
                        # minus 1 because the first row is a Header)
                        items = self.values[curr_row-1]
                        # If not all elements of the row have the same 
                        # value, set the value of the first Entries to
                        # "Multiple values" 
                        if not all(items[0] == item for item in items):
                            widget.delete(0, "end")  # Delete
                            widget.insert(0, "Multiple values")  # Readd
                            
                    # Get the Label of which the text needs to be swapped
                    elif (widget.winfo_class() == "Label" and 
                          dim == 2 and
                          widget.grid_info() and
                          widget.grid_info()['row'] == 0 and 
                          widget.grid_info()['column'] == 4):
                        # Get all Label texts
                        label_text = widget.cget('text')
                        # Swap the element accordingly
                        if label_text == "REGION 1":
                            widget['text'] = "ALL REGIONS"
                        if label_text == "ATOM 1":
                            widget['text'] = "ALL ATOMS"
        # Otherwise check, if all Entry values are the same and update
        # the saved Entry values
        else:
            # Iterate through every (already placed) widget
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, info Button and the single Entry
                if i <= NUM_ELEMS:
                    continue
                elif widget.winfo_class() == "Entry" and widget.grid_info():
                    # Current column in the grid
                    curr_col = widget.grid_info()['column']
                    # Column in the array
                    col = curr_col - (NUM_ELEMS+2)
                    # Current widget value
                    curr_value = widget.get()
                    # If the value of the first Entry is not "Multiple 
                    # values", set all values of the column to match
                    # the value of the first Entry
                    if curr_value != "Multiple values":
                        for j in range(len(self.values)):
                            self.values[j][col] = curr_value
                # Get the Label of which the text needs to be swapped
                elif (widget.winfo_class() == "Label" and 
                      dim == 2 and
                      widget.grid_info() and
                      widget.grid_info()['row'] == 1 and 
                      widget.grid_info()['column'] == 3):
                    # Get all Label texts
                    label_text = widget.cget('text')
                    # Swap the elements back  accordingly
                    if label_text == "ALL REGIONS":
                        widget['text'] = "REGION 1"
                    if label_text == "ALL ATOMS":
                        widget['text'] = "ATOM 1"
            # Hide every widget except the main Label and info Button
            # and show the Entry
            self.hide_widgets(self, m, n, True, row_index)
            # Set the single Entry value
            self.set_entry_value(self, m, n)
            
        # Change the left arrow button to the right arrow button
        self.set_button(left_arrow_btn, "arrow_r.gif", "r")
        # Update the Button commands
        self.update_buttons_command(index_var_list)
        # Set the weigths for the new state
        self.set_weights(self, dim, IS_DOWN, False, IS_POINT)
            
    def open_index_var_d(self, index_var_list, row_index):
        """
        This method is used to expand the array of an index variable
        array parameter vertically/down.
                        
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Get the Button reference and array state
        down_arrow_btn, IS_DOWN, IS_RIGHT = self.get_state('d')
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(index_var_list)

        # If the array is collapsed currently
        if not IS_RIGHT:
            # Set the Entry values to match the single Entry
            init = self.set_entry_values(self)
            # Save the Entry values
            self.save_entry_values(self, m, n, init, IS_POINT)
            # Iterate through every widget
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label and info Button
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
                    
            # Iterate through every widget and update values
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, info Button and the single Entry
                if i <= NUM_ELEMS:
                    continue
                # Get the Label of which the text needs to be swapped
                elif (widget.winfo_class() == "Label" and 
                      dim == 2 and
                      widget.grid_info() and
                      widget.grid_info()['row'] == 0 and 
                      widget.grid_info()['column'] == 4):
                    # Get all Label texts
                    label_text = widget.cget('text')
                    # Swap the element accordingly
                    if label_text == "REGION 1":
                        widget['text'] = "ALL REGIONS"
                    if label_text == "ATOM 1":
                        widget['text'] = "ALL ATOMS"
                elif widget.winfo_class() == "Entry" and widget.grid_info():
                    # Current row in the grid
                    curr_row = widget.grid_info()['row']
                    # Row in the array
                    row = curr_row - 1
                    # Array with all elements from current row
                    items = self.values[row]
                    
                    # If all items are the same, set the value
                    if all(items[0] == item for item in items):
                        widget.delete(0, "end")  # Delete
                        widget.insert(0, items[0])  # Readd
                    # Otherwise set the first Entry to "Multiple values"
                    else:
                        widget.delete(0, "end")  # Delete
                        widget.insert(0, "Multiple values")  # Readd
        # If the array is expanded to the right
        else:                              
            # Iterate through every (already placed) widget
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, info Button and the single Entry
                if i <= NUM_ELEMS:
                    continue
                # Get the Label of which the text needs to be swapped
                elif (widget.winfo_class() == "Label" and 
                      dim == 2 and
                      widget.grid_info() and
                      widget.grid_info()['row'] == 1 and 
                      widget.grid_info()['column'] == 3):
                    # Get all Label texts
                    label_text = widget.cget('text')
                    # Swap the elements back  accordingly
                    if label_text == "ALL REGIONS":
                        widget['text'] = "REGION 1"
                    if label_text == "ALL ATOMS":
                        widget['text'] = "ATOM 1"
                elif widget.winfo_class() == "Entry" and widget.grid_info():
                    # Current row and column in the grid
                    curr_row = widget.grid_info()['row']
                    curr_col = widget.grid_info()['column']
                    # Row and column in the array
                    row = curr_row - 1
                    col = curr_col - (NUM_ELEMS+2)
                    # Current widget value
                    curr_value = widget.get()
                    # If the value of the first Entry was "Multiple 
                    # values", replace it with the value when expanding
                    if curr_value == "Multiple values":
                        widget.delete(0, "end")  # Delete
                        widget.insert(0, self.values[row][col])  # Readd
                    # Otherwise set all values in the current column, 
                    # to match the value of the first Entry
                    else:
                        for j in range(len(self.values)):
                            self.values[j][col] = curr_value
            # Iterate through every widget
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label and info Button
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
                    
                    if widget.winfo_class() == "Entry" and widget.grid_info():
                        # Row and column in the array
                        row = curr_row - 1
                        col = curr_col - (NUM_ELEMS+2)
                        # Current widget value
                        curr_value = widget.get()
                        # If the current widget value is not up to date
                        if curr_value != self.values[row][col]:
                            widget.delete(0, "end")  # Delete
                            widget.insert(0, self.values[row][col])  # Readd
                
        # Change the down arrow button to an up arrow button
        self.set_button(down_arrow_btn, "arrow_u.gif", "u")
        # Update the Button commands
        self.update_buttons_command(index_var_list)
        # Set the weigths for the new state
        self.set_weights(self, dim, True, IS_RIGHT, IS_POINT)

    def close_index_var_u(self, index_var_list, row_index):
        """
        This method is used to collapse the array of an index variable
        array parameter vertically/up.
                        
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """
        # Get the Button reference and array state
        up_arrow_btn, IS_DOWN, IS_RIGHT = self.get_state('u')
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(index_var_list)        

        # If the array is expanded to the right, readd the widgets
        if IS_RIGHT:
            # Save the current values of the index variable array
            self.save_entry_values(self, m, n, False, IS_POINT)
            # Hide every widget except the main Label and info Button 
            # and show the Entry
            self.hide_widgets(self, m, n, True, row_index)  
            # Iterate through every widget
            for i,widget in enumerate(self.children.values()):
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
                
                    # Because of the if condition above, only 
                    # the Entries of the first row are checked
                    if widget.winfo_class() == "Entry":
                        # Get the values of the according column (column
                        # num minus (n+1) + (NUM_ELEMS+2) because the 
                        # first row is a Header and the first Entry 
                        # column is at NUM_ELEMS + 2 )
                        col = i-(n+1)-(NUM_ELEMS+2)
                        items = [x[col] for x in self.values]
                        # If not all elements of the column have the  
                        # same value, set the value of the first Entries
                        # to "Multiple values" 
                        if not all(items[0] == item for item in items):
                            widget.delete(0, "end")  # Delete
                            widget.insert(0, "Multiple values")  # Readd
                    # Get the Label of which the text needs to be swapped
                    elif (widget.winfo_class() == "Label" and 
                          dim == 2 and
                          widget.grid_info() and
                          widget.grid_info()['row'] == 1 and 
                          widget.grid_info()['column'] == 3):
                        # Get all Label texts
                        label_text = widget.cget('text')
                        # Swap the element accordingly
                        if label_text == "REGION 1":
                            widget['text'] = "ALL REGIONS"
                        if label_text == "ATOM 1":
                            widget['text'] = "ALL ATOMS"  

                    
        # Otherwise check, if all Entry values are the same
        else:
            if IS_POINT:
                # Save the current values of the index variable array
                self.save_entry_values(self, m, n, False, IS_POINT)
            # Iterate through every (already placed) widget
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, info Button and the single Entry
                if i <= NUM_ELEMS:
                    continue
                elif widget.winfo_class() == "Entry" and widget.grid_info():
                    # Current row and column in the grid
                    curr_row = widget.grid_info()['row']
                    curr_col = widget.grid_info()['column']
                    # Row and column in the array
                    row = curr_row - 1
                    col = curr_col - (NUM_ELEMS+2)
                    # Current widget value
                    curr_value = widget.get()
                    # If the value of the first Entry is not "Multiple 
                    # values", but a value, set all values of the row
                    # to match the value of the first Entry
                    if curr_value != "Multiple values":
                        for j in range(len(self.values[row])):
                            self.values[row][j] = curr_value
                # Get the Label of which the text needs to be swapped
                elif (widget.winfo_class() == "Label" and 
                      dim == 2 and
                      widget.grid_info() and
                      widget.grid_info()['row'] == 0 and 
                      widget.grid_info()['column'] == 4):
                    # Get all Label texts
                    label_text = widget.cget('text')
                    # Swap the elements back  accordingly
                    if label_text == "ALL REGIONS":
                        widget['text'] = "REGION 1"
                    if label_text == "ALL ATOMS":
                        widget['text'] = "ATOM 1"
                            
            # Hide every widget except the main Label and info Button
            # and show the Entry
            self.hide_widgets(self, m, n, True, row_index)
            # Set the single Entry value
            self.set_entry_value(self, m, n)
                
        # Change the up arrow button to the down arrow button
        self.set_button(up_arrow_btn, "arrow_d.gif", "d")
        # Update the Button commands
        self.update_buttons_command(index_var_list)
        # Set the weigths for the new state
        self.set_weights(self, dim, False, IS_RIGHT, IS_POINT)
                                                
    def add_row(self, index_var_list, row_index):
        """
        This method is used to add a row for the POINT index variable
        array.
                        
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """        
        # Iterate through every widget
        for widget in self.children.values():
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
        self.parent.add_label(parent=self, 
                              label_text="POINT " + str(self.num_points))
        self.parent.add_entry(parent=self, par_name='POS', 
                              entry_text="", add_to_list = False)
        # Add the remove Button
        button_remove = self.parent.add_button(parent=self, btn_text="-",
                                               w=ARROW_WIDTH, h=ARROW_HEIGHT)
        self.set_button(button_remove, "minus.gif", '-')
                    
        # Get the dimensions for the array to be created
        dim, m, n, IS_POINT = self.get_dimensions(index_var_list)
        
        # Add the '+' and the down/up arrow Button
        button_add = self.parent.add_button(parent=self, btn_text="+",
                                            w=ARROW_WIDTH, h=ARROW_HEIGHT)
        self.set_button(button_add, "add.gif", '+')
        button_add.grid(row=row_index ,column=7 - 2)
         
        button_arrow = self.parent.add_button(parent=self, btn_text="",
                                              w=ARROW_WIDTH, h=ARROW_HEIGHT)
        if IS_DOWN:            
            self.set_button(button_arrow, "arrow_u.gif", 'u')
        else:
            self.set_button(button_arrow, "arrow_d.gif", 'd')
            
        button_arrow.grid(row=row_index ,column=7 - 1)
            
        # If the array is expanded downwards
        if IS_DOWN:
            # Hide every widget except the main Label and info Button
            self.hide_widgets(self, m, n)
            # Iterate through every widget, and readd them
            for i,widget in enumerate(self.children.values()):
                # Skip the main Label, the info Button and the Entry
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
        self.update_buttons_command(index_var_list)
        # Set the weigths for the new state
        self.set_weights(self, dim, IS_DOWN, False, True)
            
    def delete_row(self, index_var_list, row_index):
        """
        This method is used to delete a row for index variable arrays
        for the POINT parameter.
        
        :param index_var_list: the List of index variable elements for
                               the current parameter
        :param row_index: the index of the current row
        """        
        # Iterate through every widget
        for widget in self.children.values():
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
        dim, m, n, IS_POINT = self.get_dimensions(index_var_list)
 
        # Hide every widget except the main Label and info Button
        self.hide_widgets(self, m, n)
        # Iterate through every widget, and readd them
        for i,widget in enumerate(self.children.values()):
            # Skip the main Label, the info Button and the Entry
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
        for i,widget in enumerate(self.children.values()):
            if i < NUM_ELEMS+5 or not widget.grid_info():
                continue            
            elif (widget.winfo_class() == "Label" and 
                  "POINT" in widget.cget('text')):
               widget.config(text=('POINT ' + str(widget.grid_info()['row'])))

        # Update the Button commands
        self.update_buttons_command(index_var_list)

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

    def save_entry_values(self, par_frame, m ,n, init=False, IS_POINT=False):
        """
        This method is used to save the values of the index variable
        array elements so they can be kept track of 
        
        :param par_frame: the parent Frame
        :param m: the number of rows in the index variable array
        :param n: the number of columns in the index variable array
        :param init: True if the array should be initialized
        :param IS_POINT: True if the parameter is POINTS (special array)
        """
        # ALways update for the POINT index variable array
        if IS_POINT:
            par_frame.values = [[ None for y in range(n-1) ] for x in range(m)]
        
            j = 0
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label, info Button and the single Entry
                if i <= NUM_ELEMS:
                    continue
                # Save the value of all other Entry widgets
                elif widget.winfo_class() == "Entry":
                    curr_val = widget.get()                
                    # Do not overwrite the old values with the text 
                    # "Multiple values"
                    if curr_val != "Multiple values":
                        par_frame.values[j//(n-1)][j%(n-1)]  = curr_val
                    j += 1
            return
            
        # If the Array does not exist yet
        if not par_frame.values:
            par_frame.values = [[ None for y in range(n) ] for x in range(m)]
        # If the array should be changed
        if not init or any(None in x for x in par_frame.values):
            j = 0
            # Iterate through every widget
            for i,widget in enumerate(par_frame.children.values()):
                # Skip the main Label, info Button and the single Entry
                if i <= NUM_ELEMS:
                    continue
                # Save the value of all other Entry widgets
                elif widget.winfo_class() == "Entry":
                    curr_val = widget.get()                
                    # Do not overwrite the old values with the text 
                    # "Multiple values"
                    if curr_val != "Multiple values":                
                        par_frame.values[j//n][j%n]  = curr_val
                    j += 1            

    def set_entry_values(self, par_frame):
        """
        This method is used to set the values of the index variable
        array elements to match the value of the single Entry
        
        :param par_frame: the parent Frame
        """
        # Iterate through every widget
        for i,widget in enumerate(par_frame.children.values()):
            # Skip the main Label and info Button
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
        
        if curr_val != "Multiple values":
            return False
        else:
            return True

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
            # Skip the main Label and info Button
            if i < NUM_ELEMS:
                continue
            # Get the reference of the single Entry
            elif i == NUM_ELEMS:
                curr_widget = widget
            # Get the value of all other Entry widgets
            elif (i < (NUM_ELEMS+1) + (m+1)*(n+1) and 
                      widget.winfo_class() == "Entry"):
                items.append(widget.get())

        # Set the value of the singel Entry
        curr_widget.delete(0, "end")  # Delete
        if all(items[0] == item for item in items):
            curr_widget.insert(0, items[0])  # Readd 
        else:
            curr_widget.insert(0, "Multiple values")  # Readd

    def hide_widgets(self, par_frame, m, n, showEntry=False, row_index=None):
        """
        This method is used to hide the widgets in the index variable
        array of the IndexVariableArrayFrame.
        
        :param par_frame: the parent Frame
        :param m: the number of rows of the index variable array
        :param n: the number of columns of the index variable array
        :param showEntry: the option to show the single Entry
        :param row_index: the row of the single Entry
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

    def get_dimensions(self, index_var_list):
        """
        Get the dimensions of the index variable array to be created.
        
        Get the dimensions of the index variable array, depending on 
        the number of parameters in the index_var_list. Additionally,
        consider the parameters themselves.
        
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
            elif "REGION" in index_var_list and "geom" in str(self):
                # Create an NR x 1 array in the geom tab 
                m = self.n_r + 1  # Add 1 row for REGION 0
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
    
    def get_state(self, text):
        """
        This method is used to get the current state of an index
        variable array as well as the reference to the desired button.
        
        :param text: the text to identify the Button (e.g. 'r')
        """
        IS_DOWN = False
        IS_RIGHT = False
        
        for widget in self.children.values():
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
