import os
import platform
import Pmw
import tkinter as tk
from tkinter import messagebox

from data_model.data_list import DataList
from UI.canvas.blanc_canvas import BlancCanvas
from UI.frames.blanc_frame import BlancFrame
from UI.frames.ivarray_frame import IndexVariableArrayFrame
from UI.frames.blanc_frame import MAIN as MAIN
from UI.frames.blanc_frame import BOOLEAN as BOOLEAN
from UI.frames.blanc_frame import ENTRY as ENTRY

OS = platform.system()

# Configure the width and height of the widgets
INFO_WIDTH = 10 # info Button width
INFO_HEIGHT = 10 # info Button height

# Number of parameters per row for each type of parameter
BOOL_PARAMS_PER_ROW = 4
ENTRY_PARAMS_PER_ROW = 2
# Number of elements (columns) per parameter. Currently three
# elements are used: Label, info Button, Entry/Checkbox
ELEMENTS_PER_PARAM = 3


class ScrollFrame(BlancFrame):
    """
    Scrollable Frame for one IMSIL record.

    The ScrollFrame holds the Boolean and the Entry BlancFrames,
    as well as all IndexVariableArrayFrames of the (parent) tab.

    """
    def __init__(self, parent, nr, natom, *args, **kwargs):
        """
        In the initialization of the ScrollFrame all object parameters are
        defined, the Boolean and Entry BlancFrames are created and added to
        the list of all Frames, and the scrollable area is created.

        :param parent: the parent tk widget
        :param nr: (textvariable) number of regions for index variable arrays
        :param natom: (textvariable) number of atoms for index variable arrays
        :param args: is forwarded to the super().__init__() function
        :param kwargs: is forwarded to the super().__init__() function
        """
        super().__init__(parent, *args, **kwargs)

        # Assign the number of Regions and Atoms
        self.nr = nr.get()
        self.natom = natom.get()
        self.nr_new = self.nr
        self.natom_new = self.natom

        # Define the number of columns for the Boolean and Entry params
        self.columns_b = BOOL_PARAMS_PER_ROW * ELEMENTS_PER_PARAM
        self.columns_e = ENTRY_PARAMS_PER_ROW * ELEMENTS_PER_PARAM
        # The number of columns for index variable arrays as well as the
        # Frames for each index variable array parameter are created
        # dynamically

        # Initialize the counter variable to track the number of
        # parameters in the current row
        self.params_in_row = 0
        # Initialize the counter variables for each type of parameter
        self.num_bools = 0
        self.num_entries = 0
        self.num_ivarrays = 0

        # Create the lists holding the Frames
        #TODO: par_frame_list could possibly be eliminated
        self.par_frame_list = []
        self.ui_data_list = DataList()
        # List that stores the IndexVariableArrays, to access them easier
        self.ivarray_list = []

        # Build the scrolling area
        self.main_canvas = BlancCanvas(self, columns=1, width=890)
        self.content_frame = BlancFrame(self.main_canvas, frame_id=MAIN)
        # parameter 'tags' is later required to change the window size:
        self.main_canvas.create_window(0, 0,
                                       window=self.content_frame,
                                       tags="self.content_frame",
                                       anchor="nw")
        self.vertical_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="NES")
        self.vertical_scrollbar.config(command=self.main_canvas.yview)
        self.main_canvas.config(yscrollcommand=self.vertical_scrollbar.set)
        self.bind_mouse_event(self.content_frame)

        # Create the Boolean and Entry frames
        self.content_frame_bool = BlancFrame(self.content_frame,
                                             columns=self.columns_b,
                                             frame_id=BOOLEAN)
        self.content_frame_bool.grid(sticky="NESW")

        self.content_frame_entry = BlancFrame(self.content_frame,
                                              columns=self.columns_e,
                                              frame_id=ENTRY)
        self.content_frame_entry.grid(sticky="NESW")
        # Each index variable array will get its own frame, so these frames
        # can be created only when these parameters are added.

        # Add the two Frames to the list of Frames
        self.par_frame_list.append(self.content_frame_bool)
        self.par_frame_list.append(self.content_frame_entry)

        # Update the UI
        self.content_frame.update_idletasks()
        self.content_frame.bind("<Configure>", self.update_scrollregion)
        self.main_canvas.bind('<Configure>', self.update_frame_width)

    #TODO: add_content_in_par_frame could possibly be merged into add_parameter
    def add_content_in_par_frame(self, par_name, index_var_list, default_value,
                                 short_desc, long_desc, is_bool, is_index_var,
                                 row_index):
        """
        Add the parameter to the corresponding content Frame.

        :param par_name: the parameter name
        :param index_var_list: the list of all index variables for this
                               parameter
        :param default_value: the default value of the parameter
        :param short_desc: the short description of the parameter
        :param long_desc: the long description of the parameter
        :param is_bool: True if the parameter is a boolean, False otherwise
        :param is_index_var: True if the parameter is an index variable
                             array parameter, False otherwise
        :param row_index: the row number where the parameter should
                          be placed
        """
        # Check the type of the parameter
        if is_index_var:
            # If it is an index variable array parameter, create a new
            # IndexVariableArrayFrame
            par_frame = IndexVariableArrayFrame(self, par_name,
                                                index_var_list, default_value,
                                                short_desc, long_desc,
                                                row_index,
                                                self.nr, self.natom)

            # Place the new Frame and set up the mouse bind event
            par_frame.grid(sticky="NESW")
            self.bind_mouse_event(par_frame)
            # Add the new Frame to the list of Frames
            self.par_frame_list.append(par_frame)

            # Add the IndexVariableArray to the ivarray_list to make it
            # easily accessible from the outside
            self.ivarray_list.append(par_frame)

        # If the parameter is a Boolean (Checkbutton)
        elif is_bool:
            # Set the boolean Frame as the parent Frame
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
            # Add the info Button for the parameter
            btn_info = self.add_button(parent=par_frame,
                                       w=INFO_WIDTH,
                                       h=INFO_HEIGHT,
                                       tool_tip_text=short_desc)
            self.photo = tk.PhotoImage(
                    file=os.path.join("pics", "info_sign_1.gif"))
            btn_info.config(image=self.photo)
            btn_info.image = self.photo
            btn_info.config(takefocus=False)
            btn_info.config(
                    command=lambda: messagebox.showinfo(par_name, long_desc))
            btn_info.grid(row=row_index,
                          column=2 + ELEMENTS_PER_PARAM*self.params_in_row,
                          sticky="W")
        # If the parameter is an Entry
        else:
            # Set the Entry Frame as the parent Frame
            par_frame = self.content_frame_entry

            # Add the Label for the parameter
            label = self.add_label(parent=par_frame, label_text=par_name)
            label.grid(row=row_index,
                       column=ELEMENTS_PER_PARAM*self.params_in_row,
                       sticky="NESW")
            # Add the info Button for the parameter
            btn_info = self.add_button(parent=par_frame,
                                       w=INFO_WIDTH,
                                       h=INFO_HEIGHT,
                                       tool_tip_text=short_desc)
            self.photo = tk.PhotoImage(
                    file=os.path.join("pics", "info_sign_1.gif"))
            btn_info.config(image=self.photo)
            btn_info.image = self.photo
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
        Add a new parameter.

        This method keeps track of the number of parameters and their
        position by calculating the row index as well as the column
        index and passing the according arguments to the method
        add_content_in_par_frame.

        :param par_name: the parameter name
        :param index_var_list: the list of all index variables for this
                               parameter
        :param default_value: the default value of the parameter
        :param short_desc: the short description of the parameter
        :param long_desc: the long description of the parameter
        :param is_bool: True if the parameter is a boolean, False otherwise
        :param is_index_var: True if the parameter is an index variable
                             array parameter, False otherwise
        """
        if index_var_list is None:
            index_var_list = []

        # Check the type of the parameter
        if is_index_var:
            # Reset the counter, since there is only 1 index variable
            # parameter per row
            self.params_in_row = 0
            # Add the parameter to the content Frame
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
            self.num_ivarrays += 1
        elif is_bool:
            # If the parameter is the first boolean, reset the counter
            if self.num_bools == 0:
                self.params_in_row = 0
            # Set the boolean Frame as the parent Frame
            par_frame = self.content_frame_bool
            self.bind_mouse_event(par_frame)
            # Add the parameter to the content Frame
            self.add_content_in_par_frame(
                     par_name=par_name,
                     index_var_list=index_var_list,
                     default_value=default_value,
                     short_desc=short_desc,
                     long_desc=long_desc,
                     is_bool=is_bool,
                     row_index= self.num_bools // BOOL_PARAMS_PER_ROW,
                     is_index_var=is_index_var)
            # Increase the counters
            self.num_bools += 1
            self.params_in_row += 1
            # Fold the counter at the end of the row
            self.params_in_row = self.params_in_row % BOOL_PARAMS_PER_ROW
        else:
            # If the parameter is the first entry, reset the counter
            if self.num_entries == 0:
                self.params_in_row = 0
            # Set the entry Frame as the parent Frame
            par_frame = self.content_frame_entry
            self.bind_mouse_event(par_frame)
            # Add the parameter to the content Frame
            self.add_content_in_par_frame(
                par_name=par_name,
                index_var_list=index_var_list,
                default_value=default_value,
                short_desc=short_desc,
                long_desc=long_desc,
                is_bool=is_bool,
                row_index=self.num_entries // ENTRY_PARAMS_PER_ROW,
                is_index_var=is_index_var)
            # Increase the counters
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
        # Change the entry texts and default values of NR and NATOM to
        # the values specified in the welcome window, if the datatype
        # of the default value is not an int (if it is, it should be
        # kept as it is likely the value from the specified file)
        # TODO: consider input files
        if par_name == 'NR':
            if not isinstance(default_value, int):
                entry_text = str(self.nr)
                default_value = self.nr
        elif par_name == 'NATOM':
            if not isinstance(default_value, int):
                entry_text = str(self.natom)
                default_value = self.natom

        entry_string_var = tk.StringVar(value=entry_text)
        entry = tk.Entry(parent,
                         textvariable=entry_string_var,
                         disabledbackground=disabledbackground,
                         disabledforeground=disabledforeground)

        # Disable the fields NR, NATOM and NAME in the GUI
        if par_name == 'NR' or par_name == 'NATOM':
            entry.config(state='disabled')

        if par_name == "NAME":
            entry.config(state='readonly')

        # Adding the Entries for the index variable array "POINT" to
        # the list caused some issues. Since these are never obligatory
        # these issues can be bypassed, by not adding the Entries for
        # that index variable array to the list (add_to_list=False)
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
        Check for each tk.Entry if "obligatory if" condition is True
        or False and set the state of the tk.Entry to activate or
        deactivate the parameter.

        :par_name: Name of a bool parameter
        """
        widget_variable = self.ui_data_list.get_variable(par_name)
        obligatory_if = str(par_name + "=" + widget_variable.get())

        for ui_data in self.ui_data_list.data_list:
            if ui_data[1].winfo_class() == "Entry":
                item_name = ui_data[0]
                def_value = ui_data[3]
                if isinstance(def_value, str) and obligatory_if in def_value:
                    widgets = self.ui_data_list.get_widgets(item_name)
                    for widget in widgets:
                        widget.config(state='normal')
                elif isinstance(def_value, str) and par_name in def_value:
                    widgets = self.ui_data_list.get_widgets(item_name)
                    for widget in widgets:
                        widget.config(state='disabled')

    def update_if_obligatory_entries(self):
        """
        Update the state of a new tk.Entry.
        """
        for ui_data in self.ui_data_list.data_list:
            if ui_data[1].winfo_class() == "Checkbutton":
                # For each flag, update all entries of the parameters
                self.update_if_obligatory_entry(par_name=ui_data[0])

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

    def bind_mouse_event(self, parent):
        """
        The bind_mouse_event binds the mouse scrolling event with the
        mouse_wheel function, which changes depending on the scrolling
        value the y-view of the main_canvas.
        """
        if parent is not None:
            # Add mouse scrolling event for Darwin, Windows and Linux
            if OS == 'Windows' or OS == 'Darwin':
                # With Windows and Mac OS (OS X)
                parent.bind(sequence="<MouseWheel>", func=self.mouse_wheel)
            else:
                # With Linux
                parent.bind(sequence="<Button-4>", func=self.mouse_wheel)
                parent.bind(sequence="<Button-5>", func=self.mouse_wheel)

    def mouse_wheel(self, event):
        if OS == 'Linux':
            if event.num == 4:
                self.main_canvas.yview_scroll(int(event.delta), "units")
            elif event.num == 5:
                self.main_canvas.yview_scroll(int(-1 * event.delta), "units")
        elif OS == 'Windows':
            self.main_canvas.yview_scroll(int(-1 * event.delta/120), "units")
        elif OS == 'Darwin':
            self.main_canvas.yview_scroll(int(-1 * event.delta), "units")

    def get_ivarrays(self):
        """
        Return IndexVariableArrays that are placed inside this Scroll_Frame.
        """
        return self.ivarray_list

    def clear_ivarray_list(self):
        """
        Clears the ivarray_list.
        """
        self.ivarray_list.clear()
