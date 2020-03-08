"""
This module defines a tk.Frame and creates for each table row a row with the
following elements: a tk.Label with the parameter name, an info Button
which pops up a window with a long description about the parameter when clicked,
a tk.Entry that contains the parameter value (or if the parameter is of type
boolean, then there is a tk.Checkbutton), for each index variable of the
current database table there is a tk.Label and tk.Entry with the index
variable name and value. At last there are two tk.Buttons (+) and (-) to
add and delete new parameters.

Furthermore the main tk.Frame contains a scrollable area containing a frame for
basic (common) parameters called self.content_frame_basic and a frame for
all other parameters called self.content_frame_adv.
With the show/hide Button the visibility of the frame with advanced parameters
can be turned on/off.
"""

import platform
import Pmw
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Widget

from DataModel.DataList import DataList
from UI.Canvas.blanc.blanc_canvas import BlancCanvas
from UI.Frames.blanc.blanc_frame import BlancFrame

OS = platform.system()


# Configure elements width
INFO_WIDTH = 10
INFO_HEIGHT = 10
ARROW_WIDTH = 25
ARROW_HEIGHT = 25

# Set the number of parameters per row for each type and the elements
# per parameter (the number of columns needed for 1 parameter)
BOOL_PARAMETERS_PER_ROW = 5
ENTRY_PARAMETERS_PER_ROW = 3
INDEX_PARAMETERS_PER_ROW = 1
ELEMENTS_PER_PARAMETER = 3

class ImsilScrollFrame(BlancFrame):
    """
    In the initialization only the scrollable area is created. Use function
    add_parameter to add new parameters to the frame.
    """

    def __init__(self, parent, index_var_list=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # save all index variables in a list
        if index_var_list is None:
            self.index_var_list = list()
        else:
            self.index_var_list = index_var_list
            

        # Define the number of columns as the product of the constants
        # defining the parameters per row and the elements per parameter.        
        self.columns_b = BOOL_PARAMETERS_PER_ROW * ELEMENTS_PER_PARAMETER
        self.columns_e = ENTRY_PARAMETERS_PER_ROW * ELEMENTS_PER_PARAMETER
        # For index variable arrays set the number of rows according
        # to the number of elements in the array (2 per element and 4
        # additional ones for the label, info and the expand buttons)
        self.columns_i =  2 * len(self.index_var_list) + 4

        # Define the counter variable to track the number of parameters in
        # the current row
        self.params_in_row = 0;

        # Use a separate frame for the three groups of parameters
        self.par_frame_list = list()
        self.ui_data_list = DataList()

        # build the scrolling area
        self.main_canvas = BlancCanvas(self, columns=1, width=890)
        self.content_frame = BlancFrame(self.main_canvas, frame_index=0)
        # @create_window: parameter 'tags' is later required to change the
        # window size
        self.main_canvas.create_window(0, 0, window=self.content_frame,
                                       tags="self.content_frame", anchor="nw")
        self.vertical_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="NES")
        self.vertical_scrollbar.config(command=self.main_canvas.yview)
        self.main_canvas.config(yscrollcommand=self.vertical_scrollbar.set)
        self.bind_mouse_event(self.content_frame)

        # Create three frames for the three different parameter types
        self.content_frame_bool = BlancFrame(self.content_frame, columns = self.columns_b, frame_index=1)
        self.content_frame_bool.grid(sticky="NESW")
        self.num_bools = 0

        self.content_frame_entry = BlancFrame(self.content_frame, columns = self.columns_e, frame_index=2)
        self.content_frame_entry.grid(sticky="NESW")
        self.num_entries = 0
        
        self.content_frame_index = BlancFrame(self.content_frame, columns = self.columns_i, frame_index=3)
        self.content_frame_index.grid(sticky="NESW")
        self.num_index = 0
        
        self.par_frame_list.append(self.content_frame_bool)
        self.par_frame_list.append(self.content_frame_entry)
        self.par_frame_list.append(self.content_frame_index)

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

    def update_buttons_command(self, par_frame_index, par_name,
                               index_var_list, default_value, short_desc,
                               long_desc, is_bool):
        """
        Go through each widget in the parameter
        frame and update the parameter values of the button commands.
        This is necessary to make sure that the right row of the
        specified parameter will be added or removed.
        """
        par_frame = self.par_frame_list[par_frame_index]
        for child in par_frame.winfo_children():
            if child.winfo_class() == 'Button':
                child_grid_row = child.grid_info()['row']
                if 'r' in child.cget('text'):
                    child.config(
                        command=lambda row_index=child_grid_row:
                        self.open_index_var_r(
                            par_frame_index=par_frame_index, par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc, is_bool=is_bool,
                            row_index=row_index,
                            is_index_var=False
                        )
                    )
                if 'l' in child.cget('text'):
                    child.config(
                        command=lambda row_index=child_grid_row:
                        self.close_index_var_l(
                            par_frame_index=par_frame_index, par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc, is_bool=is_bool,
                            row_index=row_index,
                            is_index_var=False
                        )
                    )                        
                if '-' in child.cget('text'):
                    child.config(
                        command=lambda row_index=str(child_grid_row):
                        self.remove_content_in_par_frame(
                            par_frame_index=par_frame_index, par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc, long_desc=long_desc,
                            is_bool=is_bool,
                            row_index=row_index
                        )
                    )

    def open_index_var_r(self, par_frame_index, par_name,
                                 index_var_list, default_value, short_desc,
                                 long_desc, is_bool, is_index_var, row_index):
        
        row_number = row_index
        par_frame = self.par_frame_list[par_frame_index]
#        print("Hi")
#        print(par_frame)
        temp_column_index = 0
        # add for each index variable a Label and an Entry
        for index_var in self.index_var_list:
            temp_column_index += 2
            label = self.add_label(parent=par_frame,
                                   label_text=index_var)
            label.grid(row=row_number, column=temp_column_index,
                       sticky="NESW")
            entry = self.add_entry(parent=par_frame, par_name=par_name,
                                   entry_text="")
            entry.grid(row=row_number, column=temp_column_index + 1,
                       sticky="NESW")
            if index_var not in index_var_list:
                # Disable Entry of the index variable if current
                # parameter doesn't use it
                entry.config(state='disabled')
#    
#        par_frame.update()
#        print(par_frame.winfo_children())
        #print(par_frame.children.values())
#        par_frame.children.update()
#        for widget in par_frame.children.values():
#            widget_grid_row = widget.grid_info()['row']
#            widget_grid_column = widget.grid_info()['column']
#            
#            print(widget_grid_row, widget_grid_column)
                
        button_l = self.add_button(parent=par_frame, btn_text="l",w=ARROW_WIDTH,h=ARROW_HEIGHT)
        self.photo_l=tk.PhotoImage(file="arrow_l.gif")
        button_l.config(image=self.photo_l)
        button_l.image = self.photo_l;
        button_l.config(takefocus=False)
        button_l.grid(row=row_number, column=self.columns_i - 1)
        
        
        self.update_buttons_command(par_frame_index=par_frame_index,
                            par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc, is_bool=is_bool)
        
        
    def close_index_var_l(self, par_frame_index, par_name,
                                 index_var_list, default_value, short_desc,
                                 long_desc, is_bool, is_index_var, row_index):        

        #tk.Frame.winfo_children.
        row_number = row_index
        par_frame = self.par_frame_list[par_frame_index]
        temp_column_index = 0
        par_frame.update()
        
        for widget in par_frame.children.values():            
            print(widget.grid_info())
        
        # add for each index variable a Label and an Entry
        for widget in par_frame.children.values():            
            #print(widget)
            widget_grid_row = widget.grid_info()['row']
            widget_grid_column = widget.grid_info()['column']
            
#            print(widget_grid_row, widget_grid_column)

            if widget_grid_row < row_number:
                continue
            if widget_grid_row > row_number:
                continue

            if widget_grid_column < 2:
                continue
            
            if widget_grid_column >=self.columns_i-2:
                continue
            #print(i, widget)
            
            widget.grid_forget() 
            
            if widget_grid_row == row_number and widget_grid_column == 3:
                widget.grid(row=row_number, column=2,sticky="NESW")
            
#            par_frame.
#            temp_column_index += 2
#            label = self.add_label(parent=par_frame,
#                                   label_text=index_var)
#            label.grid(row=row_number, column=temp_column_index,
#                       sticky="NESW")
#            entry = self.add_entry(parent=par_frame, par_name=par_name,
#                                   entry_text="")
#            entry.grid(row=row_number, column=temp_column_index + 1,
#                       sticky="NESW")
#            if index_var not in index_var_list:
#                # Disable Entry of the index variable if current
#                # parameter doesn't use it
#                entry.config(state='disabled')
                
        button_r = self.add_button(parent=par_frame, btn_text="r",w=ARROW_WIDTH,h=ARROW_HEIGHT)
        self.photo_r=tk.PhotoImage(file="arrow_r.gif")
        button_r.config(image=self.photo_r)
        button_r.image = self.photo_r;
        button_r.config(takefocus=False)
        button_r.grid(row=row_number, column=self.columns_i - 1)   
        
        self.update_buttons_command(par_frame_index=par_frame_index,
                            par_name=par_name,
                            index_var_list=index_var_list,
                            default_value=default_value,
                            short_desc=short_desc,
                            long_desc=long_desc, is_bool=is_bool)        

    def add_content_in_par_frame(self, par_frame_index, par_name,
                                 index_var_list, default_value, short_desc,
                                 long_desc, is_bool, is_index_var, row_index):
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
        par_frame = self.par_frame_list[par_frame_index]
        row_number = int(row_index)
                
#        if row_number > 1:
#            # move elements one row down to make place for the new row
#            for child in par_frame.winfo_children():
#                child_grid_row = child.grid_info()['row']
#                child_grid_column = child.grid_info()['column']
#                if child_grid_row >= row_number:
#                    child.grid_forget()
#                    if child.winfo_class() == 'Button':
#                        child.grid(row=child_grid_row + 1,
#                                   column=child_grid_column)
#                    else:
#                        child.grid(row=child_grid_row + 1,
#                                   column=child_grid_column, sticky="NESW")
        
               
        if is_index_var:
            
#            par_frame = BlancFrame(self.content_frame, columns = self.columns_i, frame_index=3)
#            self.content_frame_index.grid(sticky="NESW")
#            self.num_index = 0
            
            label = self.add_label(
                    parent=par_frame,
                    label_text=par_name)

            label.grid(row=row_number, column=0, sticky="NESW")
    
            # Add info button which shows details about the parameter in a message
            button_info = self.add_button(parent=par_frame,w=INFO_WIDTH,h=INFO_HEIGHT, 
                                          tool_tip_text=short_desc)
            self.photo=tk.PhotoImage(file="info_sign_1.gif")
            button_info.config(image=self.photo)
            button_info.image = self.photo;
            button_info.config(takefocus=False)
            button_info.config(
                command=lambda: messagebox.showinfo(par_name, long_desc))
            button_info.grid(row=row_number, column=1, sticky="W")
            
            
#            temp_column_index = 0
#            # add for each index variable a Label and an Entry
#            for index_var in self.index_var_list:
#                temp_column_index += 2
#                label = self.add_label(parent=par_frame,
#                                       label_text=index_var)
#                label.grid(row=row_number, column=temp_column_index,
#                           sticky="NESW")
#                entry = self.add_entry(parent=par_frame, par_name=par_name,
#                                       entry_text="")
#                entry.grid(row=row_number, column=temp_column_index + 1,
#                           sticky="NESW")
#                if index_var not in index_var_list:
#                    # Disable Entry of the index variable if current
#                    # parameter doesn't use it
#                    entry.config(state='disabled')
            
            entry = self.add_entry(parent=par_frame, par_name=par_name,
                                       entry_text="")
            entry.grid(row=row_number, column=2,
                           sticky="NESW")

            # Add "+" Button to the paramter, with which the user can add
            # a new parameter with the same name (is necessary, only if
            # there are available index variables)
            button_d = self.add_button(parent=par_frame, btn_text="d",w=ARROW_WIDTH,h=ARROW_HEIGHT)
            self.photo_d=tk.PhotoImage(file="arrow_d.gif")
            button_d.config(image=self.photo_d)
            button_d.image = self.photo_d;
            button_d.config(takefocus=False)
            button_d.grid(row=row_number, column=self.columns_i - 2)
            
            button_r = self.add_button(parent=par_frame, btn_text="r",w=ARROW_WIDTH,h=ARROW_HEIGHT)
            self.photo_r=tk.PhotoImage(file="arrow_r.gif")
            button_r.config(image=self.photo_r)
            button_r.image = self.photo_r;
            button_r.config(takefocus=False)
            button_r.grid(row=row_number, column=self.columns_i - 1)



#            # Add "-" Button with which the user can delete a paramter
#            button_minus = self.add_button(parent=par_frame, btn_text="-")
#            if row_number is 1:
#                # To prevent that the user can delete all parameters. The
#                # first parameter cannot be deleted
#                button_minus.config(state=tk.DISABLED)
#            button_minus.grid(row=row_number, column=self.columns_i - 1)
        # If the parameter is a boolean (Checkbutton)
        elif is_bool:
            # Add Checkbutton for boolean parameter            
            checkbutton = self.add_checkbutton(parent=par_frame,
                                               par_name=par_name,
                                               #width=width,
                                               cb_value=default_value,
                                               default_value=default_value)
            checkbutton.grid(row=row_number, column=0+ELEMENTS_PER_PARAMETER*self.params_in_row, sticky="NESW")
            
            label = self.add_label(
                    parent=par_frame,
                    label_text=par_name)
            
            label.grid(row=row_number, column=1+ELEMENTS_PER_PARAMETER*self.params_in_row, sticky="NESW")
    
            # Add info button which shows details about the parameter in a message
            button_info = self.add_button(parent=par_frame,w=INFO_WIDTH,h=INFO_HEIGHT, 
                                          tool_tip_text=short_desc)
            self.photo=tk.PhotoImage(file="info_sign_1.gif")
            button_info.config(image=self.photo)
            button_info.image = self.photo;
            button_info.config(takefocus=False)
            button_info.config(
                command=lambda: messagebox.showinfo(par_name, long_desc))
            button_info.grid(row=row_number, column=2+ELEMENTS_PER_PARAMETER*self.params_in_row, sticky="W")
            
        else:
            label = self.add_label(parent=par_frame,
                       label_text=par_name)
            
            label.grid(row=row_number, column=0+ELEMENTS_PER_PARAMETER*self.params_in_row, sticky="NESW")
    
            # Add info button which shows details about the parameter in a message
            button_info = self.add_button(parent=par_frame,w=INFO_WIDTH,h=INFO_HEIGHT, 
                                          tool_tip_text=short_desc)
            self.photo=tk.PhotoImage(file="info_sign_1.gif")
            button_info.config(image=self.photo)
            button_info.image = self.photo;
            button_info.config(takefocus=False)
            button_info.config(
                command=lambda: messagebox.showinfo(par_name, long_desc))
            button_info.grid(row=row_number, column=1+ELEMENTS_PER_PARAMETER*self.params_in_row)            
            
            entry = self.add_entry(parent=par_frame, par_name=par_name,
                                   entry_text=default_value,
                                   #width=width,
                                   default_value=default_value)
            entry.grid(row=row_number, column=2+ELEMENTS_PER_PARAMETER*self.params_in_row, sticky="NESW")        
        

        # update buttons command
        self.update_buttons_command(par_frame_index=par_frame_index,
                                    par_name=par_name,
                                    index_var_list=index_var_list,
                                    default_value=default_value,
                                    short_desc=short_desc,
                                    long_desc=long_desc, is_bool=is_bool)
        
#        if not is_index_var:
#            #print(self.params_in_row)
#            #print(len(par_frame.winfo_children()))
#            children_widgets = par_frame.winfo_children()
#            print(children_widgets)

    def remove_content_in_par_frame(self, par_frame_index, par_name,
                                    index_var_list, default_value,
                                    short_desc, long_desc, is_bool, row_index):
        """
        Take the parameter frame from the parameter frame list at the index
        par_frame_index and remove the row with the index row_index. If there
        are widgets in rows with index greater than row_index,
        these widgets are moved one row up.

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
        par_frame = self.par_frame_list[par_frame_index]
        row_number = int(row_index)

        for child in par_frame.winfo_children():
            child_grid_row = child.grid_info()['row']
            child_grid_column = child.grid_info()['column']
            if child_grid_row is row_number:
                # delete all elements in the row
                child.destroy()
            elif child_grid_row > row_number:
                # move all elements under the row one row up
                child.grid_forget()
                if child.winfo_class() == 'Button':
                    child.grid(row=child_grid_row - 1,
                               column=child_grid_column)
                else:
                    child.grid(row=child_grid_row - 1,
                               column=child_grid_column, sticky="NESW")
        # update buttons command
        self.update_buttons_command(par_frame_index=par_frame_index,
                                    par_name=par_name,
                                    index_var_list=index_var_list,
                                    default_value=default_value,
                                    short_desc=short_desc,
                                    long_desc=long_desc, is_bool=is_bool)

    def add_parameter(self, par_name, index_var_list=None, default_value="",
                      short_desc="", long_desc="", is_bool=False,
                      is_index_var=False):
        """
        Create a new frame for the given parameter, add it to the parameter
        frame list and add it to the scrollable frame to make it visible for
        the user.

        :param par_name: name of the parameter
        :param index_var_list: list of all index variables for this parameter
        :param default_value: default value of the parameter
        :param short_desc: short description of the parameter
        :param long_desc: long description of the parameter
        :param is_bool: true, if the parameter is of type bool, false else
        :param is_basic: true, if the parameter is basic, then it will be
            placed to the basic content frame that is above the advanced
            content frame. False, to add it to the advanced content frame
        """

        
        if index_var_list is None:
            index_var_list = list()
        
        # Check if there is an index variable parameter on the given 
        # page of the notebook
        #if index_var_list:
        if is_index_var:
            self.params_in_row = 0
            par_frame = self.content_frame_index
            self.bind_mouse_event(par_frame)
            self.add_content_in_par_frame(
                par_frame_index=2,
                par_name=par_name,
                index_var_list=index_var_list,
                default_value=default_value,
                short_desc=short_desc,
                long_desc=long_desc,
                is_bool=is_bool,
                row_index= self.num_index//INDEX_PARAMETERS_PER_ROW,
                is_index_var=is_index_var)
            self.num_index += 1
        elif is_bool:
            if self.num_bools == 0:
                self.params_in_row = 0
            par_frame = self.content_frame_bool
            self.bind_mouse_event(par_frame)
            self.add_content_in_par_frame(
                     par_frame_index=0,
                     par_name=par_name,
                     index_var_list=index_var_list,
                     default_value=default_value,
                     short_desc=short_desc,
                     long_desc=long_desc,
                     is_bool=is_bool,
                     row_index= self.num_bools//BOOL_PARAMETERS_PER_ROW,
                     is_index_var=is_index_var)
            self.num_bools += 1
            self.params_in_row += 1
            self.params_in_row = self.params_in_row%BOOL_PARAMETERS_PER_ROW          
        else:
            if self.num_entries == 0:
                self.params_in_row = 0
            par_frame = self.content_frame_entry
            self.bind_mouse_event(par_frame)
            self.add_content_in_par_frame(
                par_frame_index=1,
                par_name=par_name,
                index_var_list=index_var_list,
                default_value=default_value,
                short_desc=short_desc,
                long_desc=long_desc,
                is_bool=is_bool,
                row_index= self.num_entries//ENTRY_PARAMETERS_PER_ROW,
                is_index_var=is_index_var)
            self.num_entries += 1
            self.params_in_row += 1       
            self.params_in_row = self.params_in_row%ENTRY_PARAMETERS_PER_ROW
                            
                

    def add_button(self,parent,btn_text="Button",w=3,h=3,tool_tip_text = None):
        btn = tk.Button(parent, text=btn_text, width=w, height=h)
        if tool_tip_text != None:
            balloon = Pmw.Balloon(btn)
            balloon.bind(btn, tool_tip_text)
        self.bind_mouse_event(btn)
        return btn

    def add_label(self, parent, label_text, 
                  label_text_anchor=tk.W):
        label = tk.Label(parent, text=label_text,
                         anchor=label_text_anchor)
        self.bind_mouse_event(label)
        return label

    def add_entry(self, parent, par_name, entry_text,
                  default_value="", tool_tip_text="",
                  disabledbackground="gray", disabledforeground="white"):
        entry_string_var = tk.StringVar(value=entry_text)
        entry = tk.Entry(parent, textvariable=entry_string_var,
                         disabledbackground=disabledbackground,
                         disabledforeground=disabledforeground)
        self.ui_data_list.add(par_name=par_name, tk_widget=entry,
                              widget_variable=entry_string_var,
                              default_value=default_value)
        self.update_if_obligatory_entries()
        if tool_tip_text != "":
            balloon = Pmw.Balloon(entry)
            balloon.bind(entry, tool_tip_text)
        self.bind_mouse_event(entry)
        return entry

    def add_checkbutton(self, parent, par_name, 
                        cb_value="T",
                        default_value="",
                        on_value="T", off_value="F"):
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
                self.main_canvas.yview_scroll(int(event.delta), "units")
            elif event.num == 5:
                self.main_canvas.yview_scroll(int(-1 * event.delta), "units")

        elif OS == 'Windows':
            self.main_canvas.yview_scroll(int(-1 * event.delta / 120), "units")

        elif OS == 'Darwin':
            self.main_canvas.yview_scroll(int(-1 * event.delta), "units")
