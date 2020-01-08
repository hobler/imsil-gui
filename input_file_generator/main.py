"""

"""
import os
import sys
import tkinter as tk

from collections import OrderedDict
from tkinter import ttk, filedialog

from DataModel.InputFile import InputFile
from DataModel.Table.SqliteMaster import SqliteMaster
from UI.Frames.blanc.blanc_frame import BlancFrame
from UI.Frames.db_frame import DbFrame

DATABASE_FILE = "parameters.db"


def read_existing_input_file(file_path):
    """
    Use the path file_path to read the
    file and try to read it with the f90nml package in the InputFile class.

    It can be used for further work reading an input file and fill the
    GUI with the parameter values from the file.

    :param file_path:   path of an IMSIL input file
    :return:    InputFile instance if file exist,
                None, else
    """
    if os.path.isfile(file_path):
        input_file = InputFile(file_path)
        return input_file
    else:
        print(file_path + " doesn't exist.")
        return None


def center_window(tk_window):
    """
    Place the given Tk to the center of the screen

    :param tk_window: a window of type tk.Tk
    :return:
    """
    # Hide widget
    tk_window.withdraw()
    tk_window.update_idletasks()  # Update "requested size" from geometry manager

    # Gets the requested values of the height and widht.
    window_width = tk_window.winfo_reqwidth()
    window_height = tk_window.winfo_reqheight()

    # Gets both half the screen width/height and window width/height
    position_right = int(tk_window.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(tk_window.winfo_screenheight() / 2 - window_height / 2)

    # Positions the window in the center of the page.
    tk_window.geometry("+{}+{}".format(position_right, position_down))

    # Show widget
    tk_window.deiconify()


class ImsilInputParameterEditor:
    """

    """

    def __init__(self, input_file_path, type_of_simulation):
        """

        :param input_file_path:
        :param type_of_simulation:
        """
        if not os.path.isfile(DATABASE_FILE):
            sys.exit(DATABASE_FILE + " does not exist.")

        root = tk.Tk()
        root.title('IMSIL Input Parameter Editor')
        root.resizable(False, False)

        # Create and place Notebook
        nb = ttk.Notebook(root, width=900, height=600)
        nb.grid(row=0, column=0, sticky="NESW")

        sqlite_master_table = SqliteMaster(DATABASE_FILE)
        for table_name in sqlite_master_table.get_table_names():
            nb.add(DbFrame(parent=nb,
                           db_file=DATABASE_FILE,
                           table_name=table_name,
                           type_of_simulation=type_of_simulation,
                           name=table_name),
                   text=table_name)
        center_window(root)

        # if the user select an IMSIL input file
        if input_file_path != "":
            # read IMSIL input file
            input_file = read_existing_input_file(input_file_path)
            if input_file is not None:
                # got through all parameters that are defined in the file
                for key in input_file.file.keys():
                    for par_name in input_file.file[key]:
                        if not isinstance(par_name, OrderedDict):
                            # print all parameters the name and value
                            print("par_name: ", par_name, ", ",
                                  "par_value: ",
                                  input_file.file[key][par_name])
        root.mainloop()

    @staticmethod
    def get_all_parameter_values(parent):
        """
        Go through all tabs in notebook and get changes

        :param parent:
        :return:
        """
        nb_tabs = parent.tabs()
        if len(nb_tabs) > 1:
            for nb_tab in nb_tabs:
                frame = parent.nametowidget(nb_tab)
                if hasattr(frame, 'get_ui_data_list'):
                    # print(frame.get_ui_data_list())
                    pass

    @staticmethod
    def set_parameter_value(notebook_widget, tab_name, parameter_name,
                            parameter_value):
        """
        Set value of specified parameter name in the tab of the notebook with
        the name tab_name.

        Currently this function is not in use!

        :param notebook_widget:
        :param tab_name:
        :param parameter_name:
        :param parameter_value:
        :return:

        EXAMPLE:
            set_parameter_value("setup", "ndim", "2")

        Args:
            notebook_widget:
            tab_name:
            parameter_name:
            parameter_value:
        """
        nb_tabs = notebook_widget.tabs()
        # print(nb_tabs)
        frame = notebook_widget.nametowidget(tab_name)
        if frame:
            ui_data_list = frame.get_ui_data_list()
            par_variable = ui_data_list.get_variable(
                parameter_name)
            if par_variable is not None:
                par_variable.set(parameter_value)
            else:
                print(
                    "There is no parameter with the name " + parameter_name +
                    " in tab " + tab_name)
        else:
            print("There is no tab with the name " + tab_name)


class WelcomeWindow(tk.Tk):
    """
    This is a class for the welcome window.

    It contains a header text, a welcome message, a combobox where the
    user can select a specific type of simulation, an option to load an
    existing IMSIL input file and a button to open the IMSIL input parameter
    editor.

    @type of simulation: based on this option, the input file generator
    will have different parameters at the beginning of each notebook page.
    These parameters, so called "basic" parameters, that are for this
    type of simulation common, has to be defined in the database.
    """
    WINDOW_WIDTH = 500

    def __init__(self):
        super().__init__()
        self.title("Welcome")
        self.resizable(False, False)
        self.frame = BlancFrame(self, columns=3)

        # Add header
        self.header_label = tk.Label(
            self.frame,
            font="Helvetica 18 bold",
            text="IMSIL input file generator",
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="NESW")

        # Add welcome message
        self.welcome_message_label = tk.Label(
            self.frame, wraplength=self.WINDOW_WIDTH, anchor=tk.NW,
            text="Welcome to the input file generator for IMSIL. "
                 "With this tool you can generate an input file for IMSIL. "
                 "You can also edit an existing input file by loading it in "
                 "this window below.",
            justify=tk.LEFT,
        ).grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="NESW")

        # Add Listbox with elements that can be choose by the user
        self.type_sim_combobox_variable = tk.StringVar()
        self.choose_type_sim_label = tk.Label(
            self.frame,
            text="Choose type of simulation:"
        ).grid(row=2, column=0, padx=5, sticky="NES")
        self.type_sim_combobox = ttk.Combobox(
            self.frame, values=["", "any"],
            textvariable=self.type_sim_combobox_variable
        ).grid(row=2, column=1, columnspan=2, padx=(0, 10), sticky="NESW")

        # Add entry with button where the user can choose an existing file
        self.choose_existing_file_label = tk.Label(
            self.frame,
            text="Load existing input file:"
        ).grid(row=3, column=0, padx=5, pady=5, sticky="NES")
        self.choose_existing_file_variable = tk.StringVar()
        self.choose_existing_file_entry = tk.Entry(
            self.frame, textvariable=self.choose_existing_file_variable
        ).grid(row=3, column=1, pady=5, sticky="NESW")
        self.choose_existing_file_button = tk.Button(
            self.frame, text="Load",
            command=self.load_file
        ).grid(row=3, column=2, pady=5, padx=(0, 10), sticky="NESW")

        # Add button to open the imsil input parameter editor
        self.btn_continue = tk.Button(
            self.frame, text='Open IMSIL input parameter editor', padx=10,
            command=self.open_imsil_input_parameter_editor, pady=10
        ).grid(row=4, column=0, columnspan=3, padx=10, pady=10,
               sticky="NESW")

        # center the window and show it
        center_window(self)
        self.mainloop()

    def load_file(self):
        """
        Open a dialog to pick up a file. After the user select a
        file and click on the button "open" the filename will be copied
        to the entry to show the user that the file was successfully
        selected.
        """
        loaded_file = filedialog.askopenfile(
            initialdir=self.choose_existing_file_variable.get(),
            title="Select IMSIL input file")
        if loaded_file:
            self.choose_existing_file_variable.set(loaded_file.name)
            loaded_file.close()

    def open_imsil_input_parameter_editor(self):
        """
        Close this window and open
        the IMSIL input file generator with the specified parameters by
        the user. These are the path of an existing input file and the
        type of the simulation.
        """
        self.destroy()
        ImsilInputParameterEditor(
            input_file_path=self.choose_existing_file_variable.get(),
            type_of_simulation=self.type_sim_combobox_variable.get()
        )


if __name__ == '__main__':
    welcome_window = WelcomeWindow()
