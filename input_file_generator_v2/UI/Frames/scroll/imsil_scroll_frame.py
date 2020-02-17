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
from UI.Widgets.ShowAdvParButton import ShowAdvParButton, ButtonState
from UI.Frames.blanc.blanc_frame import BlancFrame

OS = platform.system()

MINUS = "-----------------------------------------"
BTN_TEXT_SHOW_ADV = MINUS + " Show advanced parameters " + MINUS
BTN_TEXT_HIDE_ADV = MINUS + " Hide advanced parameters " + MINUS

# configure elements width
PARAMETER_NAME_LABEL_WIDTH = 10
#PARAMETER_NAME_LABEL_WIDTH_WITHOUT_INDEX_VARIABLES = 5
#PARAMETER_NAME_ENTRY_WIDTH = 35
PARAMETER_NAME_ENTRY_WIDTH = 33
INFO_WIDTH = 10
INFO_HEIGHT = 10
#PARAMETER_NAME_ENTRY_WIDTH_WITHOUT_INDEX_VARIABLES = 20
INDEX_VARIABLE_NAME_LABEL_WIDTH = 10
INDEX_VARIABLE_NAME_ENTRY_WIDTH = 5
#CHECKBUTTON_WIDTH = 25
CHECKBUTTON_WIDTH = 25
#CHECKBUTTON_WIDTH_WITHOUT_INDEX_VARIABLES = 21

PARAMETERS_PER_ROW = 3

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
            

        # define number of columns:
        #   the first two are for parameter name (Label) and value (Entry),
        #   for each index variable there is a need of another two columns,
        #   the info button is also in the grid (column 1)
        # If the page has no index variable array, set the number of columns
        # to 9 so 3 element can be positioned with label, info button and
        # entry. Otherwise calculate the length based on the number of 
        # index variables.
        if len(self.index_var_list) == 0:
            self.columns = 9;
        else:
            self.columns = 2 * (len(self.index_var_list) + 1) + 1

        # Define the counter variable to track the number of parameters in
        # the current row
        self.params_in_row = 0;

        # use for every parameter a separate frame
        self.par_frame_list = list()
        self.ui_data_list = DataList()

        # build the scrolling area
        self.main_canvas = BlancCanvas(self, columns=1)
        self.content_frame = BlancFrame(self.main_canvas)
        # @create_window: parameter 'tags' is later required to change the
        # window size
        self.main_canvas.create_window(0, 0, window=self.content_frame,
                                       tags="self.content_frame", anchor="nw")
        self.vertical_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="NES")
        self.vertical_scrollbar.config(command=self.main_canvas.yview)
        self.main_canvas.config(yscrollcommand=self.vertical_scrollbar.set)
        self.bind_mouse_event(self.content_frame)

        # create two frames in self.content_frame. First for basic parameters
        # and the second for advanced parameters
        self.content_frame_basic = BlancFrame(self.content_frame)#, columns=self.columns)
        self.content_frame_basic.grid(sticky="NESW")

        self.button_frame_show_adv = ShowAdvParButton(
            self.content_frame, button_text=BTN_TEXT_HIDE_ADV)
        self.button_frame_show_adv.button.configure(command=self.toggle_adv)
        self.bind_mouse_event(self.button_frame_show_adv.button)

        self.content_frame_adv = BlancFrame(self.content_frame)

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
                if '+' in child.cget('text'):
                    child.config(
                        command=lambda row_index=str(child_grid_row + 1):
                        self.add_content_in_par_frame(
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
                
        if row_number > 1:
            # move elements one row down to make place for the new row
            for child in par_frame.winfo_children():
                child_grid_row = child.grid_info()['row']
                child_grid_column = child.grid_info()['column']
                if child_grid_row >= row_number:
                    child.grid_forget()
                    if child.winfo_class() == 'Button':
                        child.grid(row=child_grid_row + 1,
                                   column=child_grid_column)
                    else:
                        child.grid(row=child_grid_row + 1,
                                   column=child_grid_column, sticky="NESW")
        
        # Add placeholder labels, so the columns are positioned correctly
        # regardless of the number of entries in the row
        p = list()
        if not is_index_var and self.params_in_row == 0:            
            p.append(self.add_label(parent=par_frame,
                                 width=10,
                                 label_text=""))
            p.append(self.add_label(parent=par_frame,
                                 width=5,
                                 label_text=""))
            p.append(self.add_label(parent=par_frame,
                                 width=25,
                                 label_text=""))
            p.append(self.add_label(parent=par_frame,
                                 width=10,
                                 label_text=""))
            p.append(self.add_label(parent=par_frame,
                                 width=5,
                                 label_text=""))
            p.append(self.add_label(parent=par_frame,
                                 width=25,
                                 label_text=""))
            p.append(self.add_label(parent=par_frame,
                                 width=10,
                                 label_text=""))
            p.append(self.add_label(parent=par_frame,
                                 width=5,
                                 label_text=""))
            p.append(self.add_label(parent=par_frame,
                                 width=25,
                                 label_text=""))        
            p[0].grid(row=row_number, column=0, sticky="NESW")
            p[1].grid(row=row_number, column=1, sticky="NESW")
            p[2].grid(row=row_number, column=2, sticky="NESW")
            p[3].grid(row=row_number, column=3, sticky="NESW")
            p[4].grid(row=row_number, column=4, sticky="NESW")
            p[5].grid(row=row_number, column=5, sticky="NESW")
            p[6].grid(row=row_number, column=6, sticky="NESW")
            p[7].grid(row=row_number, column=7, sticky="NESW")
            p[8].grid(row=row_number, column=8, sticky="NESW")
            
#            p[0].grid_forget()
#            p[1].grid_forget()
#            p[2].grid_forget()
#            p[3].destroy()
#            p[4].destroy()
#            p[5].destroy()
#            p[6].destroy()
#            p[7].destroy()
#            p[8].destroy()
            
        if not is_index_var:
            #print(self.params_in_row)
            #print(len(par_frame.winfo_children()))
            children_widgets = par_frame.winfo_children()
            children_widgets[0].destroy()
            children_widgets[1].destroy()
            children_widgets[2].destroy()
        
        # Add Label with parameter name as text
        if len(self.index_var_list) > 0:
            label = self.add_label(parent=par_frame,
                                   width=PARAMETER_NAME_LABEL_WIDTH,
                                   label_text=par_name)
        else:
            label = self.add_label(
                parent=par_frame,
                width=PARAMETER_NAME_LABEL_WIDTH,
                label_text=par_name)
        #print(0+PARAMETERS_PER_ROW*self.params_in_row)
        label.grid(row=row_number, column=0+PARAMETERS_PER_ROW*self.params_in_row, sticky="NESW")

        # Add info button which shows details about the parameter in a message
        button_info = self.add_button(parent=par_frame,w=INFO_WIDTH,h=INFO_HEIGHT, 
                                      tool_tip_text=short_desc)
        self.photo=tk.PhotoImage(file="info_sign_1.gif")
        button_info.config(image=self.photo)
        button_info.image = self.photo;
        button_info.config(takefocus=False)
        button_info.config(
            command=lambda: messagebox.showinfo(par_name, long_desc))
        button_info.grid(row=row_number, column=1+PARAMETERS_PER_ROW*self.params_in_row)

        # config column width where the button is, so it does not take too
        # much white space
        #par_frame.columnconfigure(1, weight=1)

        if is_bool:
            # Add Checkbutton for boolean parameter
            if len(self.index_var_list) > 0:
                width = CHECKBUTTON_WIDTH
            else:
                width = CHECKBUTTON_WIDTH
            
            checkbutton = self.add_checkbutton(parent=par_frame,
                                               par_name=par_name,
                                               width=width,
                                               cb_value=default_value,
                                               default_value=default_value)
            checkbutton.grid(row=row_number, column=2+PARAMETERS_PER_ROW*self.params_in_row, sticky="NESW")
        else:
            # Add Label for non boolean parameter
            if len(self.index_var_list) > 0:
                width = PARAMETER_NAME_ENTRY_WIDTH
            else:
                width = PARAMETER_NAME_ENTRY_WIDTH
            
            entry = self.add_entry(parent=par_frame, par_name=par_name,
                                   entry_text=default_value,
                                   width=width,
                                   default_value=default_value)
            entry.grid(row=row_number, column=2+PARAMETERS_PER_ROW*self.params_in_row, sticky="NESW")
        

        #if len(self.index_var_list) > 0:
        if is_index_var:
            temp_column_index = 1
            # add for each index variable a Label and an Entry
            for index_var in self.index_var_list:
                temp_column_index += 2
                label = self.add_label(parent=par_frame,
                                       width=INDEX_VARIABLE_NAME_LABEL_WIDTH,
                                       label_text=index_var)
                label.grid(row=row_number, column=temp_column_index,
                           sticky="NESW")
                entry = self.add_entry(parent=par_frame, par_name=par_name,
                                       width=INDEX_VARIABLE_NAME_ENTRY_WIDTH,
                                       entry_text="")
                entry.grid(row=row_number, column=temp_column_index + 1,
                           sticky="NESW")
                if index_var not in index_var_list:
                    # Disable Entry of the index variable if current
                    # parameter doesn't use it
                    entry.config(state='disabled')

            # Add "+" Button to the paramter, with which the user can add
            # a new parameter with the same name (is necessary, only if
            # there are available index variables)
            button_plus = self.add_button(parent=par_frame, btn_text="+")
            button_plus.grid(row=row_number, column=self.columns)

            # Add "-" Button with which the user can delete a paramter
            button_minus = self.add_button(parent=par_frame, btn_text="-")
            if row_number is 1:
                # To prevent that the user can delete all parameters. The
                # first parameter cannot be deleted
                button_minus.config(state=tk.DISABLED)
            button_minus.grid(row=row_number, column=self.columns + 1)

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
                      is_basic=True, is_index_var=False):
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
            self.params_in_row = 0;            
            par_frame = BlancFrame(self.get_parent(is_basic=is_basic),
                                   columns=self.columns, column_weight=15)
            self.bind_mouse_event(par_frame)
            self.par_frame_list.append(par_frame)
            self.add_content_in_par_frame(
                par_frame_index=len(self.par_frame_list) - 1,
                par_name=par_name,
                index_var_list=index_var_list,
                default_value=default_value,
                short_desc=short_desc,
                long_desc=long_desc,
                is_bool=is_bool,
                row_index="1",
                is_index_var=is_index_var)
        else:
            if self.params_in_row == 0:
                 par_frame = BlancFrame(self.get_parent(is_basic=is_basic),
                        columns=self.columns, column_weight=1)
                 self.bind_mouse_event(par_frame)
                 self.par_frame_list.append(par_frame)
                 self.add_content_in_par_frame(
                         par_frame_index=len(self.par_frame_list) - 1,
                         par_name=par_name,
                         index_var_list=index_var_list,
                         default_value=default_value,
                         short_desc=short_desc,
                         long_desc=long_desc,
                         is_bool=is_bool,
                         row_index="1",
                         is_index_var=is_index_var)
                 self.params_in_row += 1
            # If the next parameter is advanced but the current frame is
            # basic, start a new frame
            elif self.content_frame._nametowidget(name=self.par_frame_list[-1].winfo_parent()) != self.get_parent(is_basic=is_basic):
                 self.params_in_row = 0 
                 par_frame = BlancFrame(self.get_parent(is_basic=is_basic),
                        columns=self.columns, column_weight=15)
                 self.bind_mouse_event(par_frame)
                 self.par_frame_list.append(par_frame)
                 self.add_content_in_par_frame(
                         par_frame_index=len(self.par_frame_list) - 1,
                         par_name=par_name,
                         index_var_list=index_var_list,
                         default_value=default_value,
                         short_desc=short_desc,
                         long_desc=long_desc,
                         is_bool=is_bool,
                         row_index="1",
                         is_index_var=is_index_var)
                 self.params_in_row += 1               
            else:
                self.add_content_in_par_frame(
                    par_frame_index=len(self.par_frame_list) - 1,
                    par_name=par_name,
                    index_var_list=index_var_list,
                    default_value=default_value,
                    short_desc=short_desc,
                    long_desc=long_desc,
                    is_bool=is_bool,
                    row_index="1",
                    is_index_var=is_index_var)
                self.params_in_row += 1       
                self.params_in_row = self.params_in_row%PARAMETERS_PER_ROW
                            

                

    def add_button(self,parent,btn_text="Button",w=3,h=3,tool_tip_text = None):
        btn = tk.Button(parent, text=btn_text, width=w, height=h)
        if tool_tip_text != None:
            balloon = Pmw.Balloon(btn)
            balloon.bind(btn, tool_tip_text)
        self.bind_mouse_event(btn)
        return btn

    def add_label(self, parent, label_text, width, 
                  label_text_anchor=tk.W):
        label = tk.Label(parent, text=label_text,
                         width=width,
                         anchor=label_text_anchor)
        self.bind_mouse_event(label)
        return label

    def add_entry(self, parent, par_name, entry_text, width,
                  default_value="", tool_tip_text="",
                  disabledbackground="gray", disabledforeground="white"):
        entry_string_var = tk.StringVar(value=entry_text)
        entry = tk.Entry(parent, textvariable=entry_string_var, width=width,
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

    def add_checkbutton(self, parent, par_name, width, 
                        cb_value="T",
                        default_value="",
                        on_value="T", off_value="F"):
        cb_string_var = tk.StringVar()
        checkbutton = tk.Checkbutton(parent, text="",
                                     variable=cb_string_var,
                                     width=width,
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

    def show_basic(self):
        self.button_frame_show_adv.button.configure(
            text=BTN_TEXT_SHOW_ADV)
        self.content_frame_adv.grid_forget()

    def show_all(self):
        self.button_frame_show_adv.button.configure(
            text=BTN_TEXT_HIDE_ADV)
        self.content_frame_adv.grid(sticky="NESW")

    def toggle_adv(self):
        if self.button_frame_show_adv.is_state_show_basic():
            self.show_all()
        else:
            self.show_basic()
        self.button_frame_show_adv.toggle_state()

    def get_parent(self, is_basic=True):
        if is_basic is True:
            return self.content_frame_basic
        else:
            return self.content_frame_adv

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
