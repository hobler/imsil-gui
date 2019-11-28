import platform
import tkinter as tk
from tkinter import ttk, messagebox

import Pmw

from DataModel.DataList import DataList
from UI.Canvas.blanc.blanc_canvas import BlancCanvas
from UI.Widgets.ShowAdvParButton import ShowAdvParButton, ButtonState
from UI.Frames.blanc.blanc_frame import BlancFrame

OS = platform.system()
BTN_TEXT_SHOW_ADV = \
    "----------------------------------------- Show advanced " \
    "parameters ----------------------------------------- "
BTN_TEXT_HIDE_ADV = \
    "-----------------------------------------  Hide advanced parameters " \
    "-----------------------------------------"
PARAMETER_NAME_LABEL_WIDTH = 15
PARAMETER_NAME_LABEL_WIDTH_WITHOUT_INDEX_VARIABLES = 5
PARAMETER_NAME_ENTRY_WIDTH = 35
PARAMETER_NAME_ENTRY_WIDTH_WITHOUT_INDEX_VARIABLES = 60
INDEX_VARIABLE_NAME_LABEL_WIDTH = 10
INDEX_VARIABLE_NAME_ENTRY_WIDTH = 5
CHECKBUTTON_WIDTH = 36
CHECKBUTTON_WIDTH_WITHOUT_INDEX_VARIABLES = 61


def bind_mouse_event(parent, mode):
    """
        bind_mouse_event has to be called on each new created element in the
        frame to be able to scroll in the frame.

    :param parent:
    :param mode:
    :return:
    """
    if parent is not None:
        # add mouse scrolling for Darwin, Windows and Linux
        if OS == 'Windows' or OS == 'Darwin':
            # with Windows and Mac OS (OS X)
            parent.bind("<MouseWheel>", mode)
        else:
            # with Linux
            parent.bind("<Button-4>", mode)
            parent.bind("<Button-5>", mode)


def show_long_desc(par_name, long_desc):
    messagebox.showinfo(par_name, long_desc)


class ImsilScrollFrame(BlancFrame):
    """
        ImsilScrollFrame contains a scrollable area where is frame for basic
        (common) parameters called self.content_frame_basic and a frame for
        all other parameters called self.content_frame_adv.
    """

    def __init__(self, parent, index_var_list=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # save all index variables in a list
        if index_var_list is None:
            self.index_var_list = list()
        else:
            self.index_var_list = index_var_list

        # define number of columns:
        #   the first two are for parameter name (Label) and value (Entry)
        #   for each index variable there is a need of another two columns
        #   at least, the info button is also in the grid (column 1)
        self.columns = 2 * (len(self.index_var_list) + 1) + 1

        # use for every parameter a separate frame
        self.par_frame_list = list()
        self.ui_data_list = DataList()

        # build the scrolling area
        self.main_canvas = BlancCanvas(self)
        self.content_frame = BlancFrame(self.main_canvas)
        # @create_window: parameter 'tags' is later required to change the
        # window size
        self.main_canvas.create_window(0, 0, window=self.content_frame,
                                       tags="self.content_frame", anchor="nw")
        self.vertical_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="NES")
        self.vertical_scrollbar.config(command=self.main_canvas.yview)
        self.main_canvas.config(yscrollcommand=self.vertical_scrollbar.set)
        bind_mouse_event(self.content_frame, self.mouse_wheel)

        # create two frames in self.content_frame. First for basic parameters
        # and the second for advanced parameters
        self.content_frame_basic = BlancFrame(self.content_frame)
        self.content_frame_basic.grid(sticky="NESW")

        self.button_frame_show_adv = ShowAdvParButton(
            self.content_frame, button_text=BTN_TEXT_SHOW_ADV,
            init_state=ButtonState.SHOW_ALL)
        self.button_frame_show_adv.button.configure(command=self.toggle_adv)
        bind_mouse_event(self.button_frame_show_adv.button, self.mouse_wheel)

        self.content_frame_adv = BlancFrame(self.content_frame)

        self.content_frame.update_idletasks()
        self.content_frame.bind("<Configure>", self.update_scrollregion)
        self.main_canvas.bind('<Configure>', self.update_frame_width)

    def update_frame_width(self, event):
        self.main_canvas.itemconfig("self.content_frame", width=event.width)

    def update_scrollregion(self, event):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def update_buttons_command(self, par_frame_index, par_name,
                               index_var_list, default_value, short_desc,
                               long_desc, is_bool):
        """
            update_buttons_command go through each widget in the parameter
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
                            row_index=row_index
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
                                 long_desc, is_bool, row_index):
        """
            add_content_in_par_frame add a row in the given parameter frame
            (defined by the parameter frame index par_frame_index).
            The parameter name will be taken from the parameter par_name.
            index_var_list defines a list of index variables that are used by
            this parameter.
            Depending on is_bool the parameter will be placed in the basic
            or not basic frame of the scrollframe.
            row_index defines the row in which the parameter should be placed.
            row_index start from "1" and is handled automatically by the
            function update_buttons_command.
        """
        par_frame = self.par_frame_list[par_frame_index]
        row_number = int(row_index)

        if row_number > 1:
            # move elements one row to the button
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
        # Add Label with parameter name as text
        if len(self.index_var_list) > 0:
            label = self.add_label(parent=par_frame,
                                   width=PARAMETER_NAME_LABEL_WIDTH,
                                   label_text=par_name,
                                   tool_tip_text=short_desc)
        else:
            label = self.add_label(
                parent=par_frame,
                width=PARAMETER_NAME_LABEL_WIDTH_WITHOUT_INDEX_VARIABLES,
                label_text=par_name,
                tool_tip_text=short_desc)
        label.grid(row=row_number, column=0, sticky="NESW")

        # Add info button which show details about the parameter in a message
        button_info = self.add_button(parent=par_frame, btn_text="i", width=2)
        button_info.config(takefocus=False)
        button_info.config(command=lambda: show_long_desc(par_name,
                                                          long_desc))
        button_info.grid(row=row_number, column=1)
        # config column width where the button is, so it does not take too
        # much white space
        par_frame.columnconfigure(1, weight=1)

        if is_bool:
            # Add Checkbutton for boolean parameter
            if len(self.index_var_list) > 0:
                checkbutton = self.add_checkbutton(parent=par_frame,
                                                   par_name=par_name,
                                                   width=CHECKBUTTON_WIDTH,
                                                   cb_value=default_value,
                                                   default_value=default_value)
            else:
                checkbutton = self.add_checkbutton(
                    parent=par_frame,
                    par_name=par_name,
                    width=CHECKBUTTON_WIDTH_WITHOUT_INDEX_VARIABLES,
                    cb_value=default_value,
                    default_value=default_value)
            checkbutton.grid(row=row_number, column=2, sticky="NESW")
        else:
            # Add Label for non boolean parameter
            if len(self.index_var_list) > 0:
                entry = self.add_entry(parent=par_frame, par_name=par_name,
                                       entry_text=default_value,
                                       width=PARAMETER_NAME_ENTRY_WIDTH,
                                       default_value=default_value)
            else:
                entry = self.add_entry(
                    parent=par_frame, par_name=par_name,
                    entry_text=default_value,
                    width=PARAMETER_NAME_ENTRY_WIDTH_WITHOUT_INDEX_VARIABLES,
                    default_value=default_value)
            entry.grid(row=row_number, column=2, sticky="NESW")

        if len(self.index_var_list) > 0:
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
                    # parameter dont use it
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
                # first parameter can not be deleted
                button_minus.config(state=tk.DISABLED)
            button_minus.grid(row=row_number, column=self.columns + 1)

        # update buttons command
        self.update_buttons_command(par_frame_index=par_frame_index,
                                    par_name=par_name,
                                    index_var_list=index_var_list,
                                    default_value=default_value,
                                    short_desc=short_desc,
                                    long_desc=long_desc, is_bool=is_bool)

    def remove_content_in_par_frame(self, par_frame_index, par_name,
                                    index_var_list, default_value,
                                    short_desc, long_desc, is_bool, row_index):
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
                      is_basic=True):
        if index_var_list is None:
            index_var_list = list()
        par_frame = BlancFrame(self.get_parent(is_basic=is_basic),
                               columns=self.columns, column_weight=15)
        bind_mouse_event(par_frame, self.mouse_wheel)
        self.par_frame_list.append(par_frame)
        self.add_content_in_par_frame(
            par_frame_index=len(self.par_frame_list) - 1,
            par_name=par_name,
            index_var_list=index_var_list,
            default_value=default_value,
            short_desc=short_desc,
            long_desc=long_desc,
            is_bool=is_bool,
            row_index="1")

    def add_button(self, parent, btn_text="Button", width=3):
        btn = tk.Button(parent, text=btn_text, width=width)
        bind_mouse_event(btn, self.mouse_wheel)
        return btn

    def add_label(self, parent, label_text, width,
                  label_text_anchor=tk.E, tool_tip_text=""):
        label = tk.Label(parent, text=label_text,
                         width=width,
                         anchor=label_text_anchor)
        if tool_tip_text != "":
            balloon = Pmw.Balloon(label)
            balloon.bind(label, tool_tip_text)
        bind_mouse_event(label, self.mouse_wheel)
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
        bind_mouse_event(entry, self.mouse_wheel)
        return entry

    def add_checkbutton(self, parent, par_name, width, cb_value="T",
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
        bind_mouse_event(checkbutton, self.mouse_wheel)
        return checkbutton

    def update_if_obligatory_entry(self, par_name):
        """
            Check for each parameter if "obligatory if" condition is true or
            false and activate or deactivate the Entry of the parameter

        :param par_name:
        :return:
        """
        value = self.ui_data_list.get_variable(par_name)
        obligatory_if = str(par_name + "=" + value.get())

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

    def mouse_wheel(self, event):
        if OS == 'Linux':
            if event.num == 4:
                self.main_canvas.yview_scroll(int(event.delta), "units")
            elif event.num == 5:
                self.main_canvas.yview_scroll(int(-1 * event.delta), "units")

        elif OS == 'Windows':
            self.main_canvas.yview_scroll(int(event.delta / 120), "units")

        elif OS == 'Darwin':
            self.main_canvas.yview_scroll(int(-1 * event.delta), "units")
