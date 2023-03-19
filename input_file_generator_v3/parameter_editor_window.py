"""
Classes:
    :ImsilInputParameterEditor: Based on the four parameters (type of
                    simulation, existing input file, number of regions
                    and number of atoms) the IMSIL Input Parameter
                    Editor will be opened.
"""

import os
import tkinter as tk
from tkinter import ttk

from UI.frames.tab_frame import TabFrame
from data_model.input_file import InputFile
from utility import center_window


def read_existing_input_file(file_path):
    """
    Read an existing input file

    Use the path file_path to read the file with the f90nml package in
    the InputFile class. It can be used for further work reading an
    input file and filling the GUI with the parameter values from the
    file.

    :param file_path: path of an IMSIL input file
    :return: InputFile instance if file exist, otherwise None
    """
    if os.path.isfile(file_path):
        input_file = InputFile(file_path)
        return input_file
    else:
        print(file_path + " doesn't exist.")
        return None


class ImsilInputParameterEditor(tk.Toplevel):
    """
    This is the class for the Imsil Input Parameter Editor.

    The IMSIL Input Parameter Editor consists of a notebook with tabs,
    where each tab corresponds to a database table.
    """

    def __init__(self, type_of_simulation, input_file_path,
                 parameter_data, region_names, on_close, master=None):
        """
        In the initialization of the IMSIL Input Parameter Editor a
        notebook is added to the window. For each table of the database
        a new tab is added as a TabFrame to the notebook.

        If a path to an input file is passed, it is read and the
        parameter values will be placed into the Editor.

        :param type_of_simulation: type of the simulation
        :param input_file_path: path of an existing input file
        :param nr: (textvariable) number of regions for index variable arrays
        :param natom: (textvariable) number of atoms for index variable arrays
        """

        # Create the root window, adjust its title, make it non-resizable and
        # center it
        tk.Toplevel.__init__(self, master)
        self.title('IMSIL Advanced Input Parameter Editor')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_btn_quit)
        # Make the advanced parameter editor window modal
        self.transient(master)
        self.grab_set()
        center_window(self)

        self.on_close = on_close
        self.quit = False

        # Add a loading message (becomes visible after the user presses the
        # button to open the IMSIL Input Parameter Editor in the Welcome Window)
        label = tk.Label(self, text="Loading data...")
        label.pack()

        # Create the Notebook
        self.nb = ttk.Notebook(self, width=900, height=600)

        # convert nr and natom into int if they are string
        # if the values aren't set, use the minimum values
        # (1 region + 1 atom are nr=1 & natom=2)
        self.nr = 1
        self.natom = 2
        nr = parameter_data.get_nr()
        natom = parameter_data.get_natom()
        if type(nr) == int:
            self.nr = nr
        elif nr.isnumeric():
            self.nr = int(nr)
        if type(natom) == int:
            self.natom = natom
        elif natom.isnumeric():
            self.natom = int(natom)

        atom_names = parameter_data.get_atoms()
        for i in range(len(atom_names)):
            if len(atom_names[i]) == 2:
                atom_names[i] = atom_names[i][0] + atom_names[i][1].lower()

        # Add and populate the necessary tabs
        for tab_name in parameter_data:
            tab_frame = TabFrame(parent=self.nb,
                                 parameter_list=parameter_data[tab_name],
                                 atom_names=atom_names,
                                 region_names=region_names,
                                 type_of_simulation=type_of_simulation,
                                 nr=self.nr,
                                 natom=self.natom,
                                 tab_name=tab_name,
                                 name=tab_name)
            self.nb.add(tab_frame, text=tab_name)

        # Remove the loading message and place the notebook
        label.pack_forget()
        self.nb.grid(row=0, column=0, sticky="NESW")

        # Center the window again, since it has changed size, and show it
        center_window(self)
        master.wait_window(self)

    def set_parameter_value(self, tab_name, parameter_name, parameter_value):
        """
        Set value of a parameter in the specified tab of the notebook.

        :param tab_name: name of the notebook tab as string
        :param parameter_name: name of the parameter as string
        :param parameter_value: parameter value to be set as a string

        EXAMPLE:
            set_parameter_value("setup", "ndim", "2")
        """
        tab_frame = self.nb.nametowidget(tab_name)
        if tab_frame is not None:
            if hasattr(tab_frame.scroll_frame, 'ui_data_list'):
                par_variable = tab_frame.scroll_frame.ui_data_list.get_variable(
                    parameter_name)
                if par_variable is not None:
                    par_variable.set(parameter_value)
                else:
                    print("There is no parameter with the name "
                          + parameter_name + " in tab " + tab_name)
            else:
                print("Frame "
                      + tab_frame
                      + " does not contain an attribute with the name"
                      + " ui_data_list")
        else:
            print("There is no tab with the name " + tab_name)

    def disable_tabs(self):
        """
        Disables all Tabs of the notebook.
        """
        for i in range(len(self.nb.tabs())):
            self.nb.tab(i, state="disabled")

    def enable_tabs(self):
        """
        Enables all Tabs of the notebook.
        """
        for i in range(len(self.nb.tabs())):
            self.nb.tab(i, state="normal")

    def on_btn_quit(self):
        """
        Callback for the Cancel Button. Asks if the cancellation was intended.
        Closes the Window if the user selects "yes".
        """
        if self.quit:
            return

        self.quit = True
        mb_result = tk.messagebox.askyesnocancel(
            title="Exit Parameter Editor",
            message="Apply changes?")

        self.quit = False
        # cancel button
        if mb_result is None:
            return

        # mb_result is true if yes was selected
        self.on_close(apply=mb_result)
        self.destroy()
