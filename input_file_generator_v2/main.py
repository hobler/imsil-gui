"""
Classes:
    :WelcomeWindow: The main window, where the user can config the 
                    input parameter editor.
    :ImsilInputParameterEditor: Based on the two parameters (type of
                    simulation and existing input file) the IMSIL Input
                    Parameter Editor will be opened.
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
    Read an existing input file
    
    Use the path file_path to read the file with the f90nml package in 
    the InputFile class. It can be used for further work reading an 
    input file and filling the GUI with the parameter values from the 
    file.

    :param file_path:   path of an IMSIL input file
    :return:    InputFile instance if file exist, otherwise None
    """
    if os.path.isfile(file_path):
        input_file = InputFile(file_path)
        return input_file
    else:
        print(file_path + " doesn't exist.")
        return None


def center_window(tk_window):
    """
    Place the given Tk window to the center of the screen

    :param tk_window: a window of type tk.Tk
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
    This is a class for the Imsil Input Parameter Editor.
    
    The IMSIL Input Parameter Editor consists of a notebook with tabs,
    where each tab corresponds to a database table.
    """

    def __init__(self, type_of_simulation, input_file_path):
        """
        In the initialization of the IMSIL Input Parameter Editor a 
        notebook is added to the window. The SqliteMaster class is used
        to determinate the table names in the database. For each table 
        name a new tab is added to the notebook. Each tab contains a 
        frame of the class DbFrame.

        If a path to an input file is passed, it is read and the 
        parameter values will be placed into the Editor.

        :param type_of_simulation: type of the simulation
        :param input_file_path: path of an existing input file
        """
        if not os.path.isfile(DATABASE_FILE):
            sys.exit(DATABASE_FILE + " does not exist.")

        root = tk.Tk()
        # Adjust the title, disable resizing and center the window
        root.title('IMSIL Input Parameter Editor')
        root.resizable(False, False)
        center_window(root)
        
        # Add loading message
        label = tk.Label(root, text = "Loading data.")
        label.pack()

        # Create the Notebook
        self.nb = ttk.Notebook(root, width=900, height=600)
        
        # Add the necessary pages
        sqlite_master_table = SqliteMaster(DATABASE_FILE)
        for table_name in sqlite_master_table.get_table_names():
            self.nb.add(DbFrame(parent=self.nb,
                                db_file=DATABASE_FILE,
                                table_name=table_name,
                                type_of_simulation=type_of_simulation,
                                name=table_name),
                        text=table_name)
        
        # Remove loading message
        label.pack_forget()
        # Place the notebook
        self.nb.grid(row=0, column=0, sticky="NESW")
        

        # if the user has passed the name of an IMSIL input file
        if input_file_path != "":
            # read IMSIL input file
            input_file = read_existing_input_file(input_file_path)
            if input_file is not None:
                # go through all parameters that are defined in the file
                for key in input_file.file.keys():
                    for par_name in input_file.file[key]:
                        if not isinstance(par_name, OrderedDict):
                            # set parameter value in tab
                            self.set_parameter_value(
                                tab_name=key,
                                parameter_name=par_name,
                                parameter_value=input_file.file[key][par_name])
        
        # Center the window        
        center_window(root)
        root.mainloop()

    def get_all_parameter_values(self):
        """
        Go through all tabs in the notebook and use the ui_data_list 
        with the stored (default) values of the parameters to get all
        changes.

        This function can be used later to generate the input file.

        Currently this function is not in use!
        """
        for nb_tab in self.nb.tabs():
            frame = self.nb.nametowidget(nb_tab)
            if hasattr(frame.scroll_frame, 'ui_data_list'):
                # frame_ui_data_list = frame.scroll_frame.ui_data_list
                pass

    def set_parameter_value(self, tab_name, parameter_name, parameter_value):
        """
        Set value of specified parameter name in the tab of the 
        notebook with the name tab_name.

        :param tab_name: name of the notebook tab as string
        :param parameter_name: name of the parameter as string
        :param parameter_value: name of the parameter value to be set

        EXAMPLE:
            set_parameter_value("setup", "ndim", "2")
        """
        frame = self.nb.nametowidget(tab_name)
        if frame is not None:
            if hasattr(frame.scroll_frame, 'ui_data_list'):
                par_variable = frame.scroll_frame.ui_data_list.get_variable(
                    parameter_name)
                if par_variable is not None:
                    par_variable.set(parameter_value)
                else:
                    print("There is no parameter with the name " +
                           parameter_name + " in tab " + tab_name)
            else:
                print("Frame " + frame +
                      " does not contain an attribute with the name "
                      "ui_data_list")
        else:
            print("There is no tab with the name " + tab_name)


class WelcomeWindow(tk.Tk):
    """
    This is a class for the welcome window.

    It contains a header text, a welcome message, a combobox where the
    user can select a specific type of simulation, an option to load an
    existing IMSIL input file and a button to open the IMSIL input 
    parameter editor.

    @type of simulation: based on this option, the input parameter 
    editor will have different parameters at the beginning of each 
    notebook page. These parameters, so called "basic" parameters, that
    are for this type of simulation common, has to be defined in the 
    database.
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
        welcome_text = ("Welcome to the input file generator for IMSIL. With" 
                        "this tool you can generate an input file for IMSIL."
                         "You can also edit an existing input file by loading"
                         "it in this window below.")
        self.welcome_message_label = tk.Label(
            self.frame, 
            wraplength=self.WINDOW_WIDTH, 
            anchor=tk.NW,
            text=welcome_text,
            justify=tk.LEFT,
        ).grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="NESW")

        # Add Listbox with elements that can be chosen by the user
        self.type_sim_combobox_variable = tk.StringVar()
        self.choose_type_sim_label = tk.Label(
            self.frame,
            text="Choose type of simulation:"
        ).grid(row=2, column=0, padx=5, sticky="NES")
        self.type_sim_combobox = ttk.Combobox(
            self.frame, 
            values=["", "any"],
            textvariable=self.type_sim_combobox_variable
        ).grid(row=2, column=1, columnspan=2, padx=(0, 10), sticky="NESW")

        # Add entry with button where the user can choose an existing file
        self.choose_existing_file_label = tk.Label(
            self.frame,
            text="Load existing input file:"
        ).grid(row=3, column=0, padx=5, pady=5, sticky="NES")
        self.choose_existing_file_variable = tk.StringVar()
        self.choose_existing_file_entry = tk.Entry(
            self.frame, 
            textvariable=self.choose_existing_file_variable
        ).grid(row=3, column=1, pady=5, sticky="NESW")
        self.choose_existing_file_button = tk.Button(
            self.frame, 
            text="Load",
            command=self.load_file
        ).grid(row=3, column=2, pady=5, padx=(0, 10), sticky="NESW")

        # Add button to open the imsil input parameter editor
        self.btn_continue = tk.Button(
            self.frame, 
            text='Open IMSIL input parameter editor', 
            padx=10,
            pady=10,
            command=self.open_imsil_input_parameter_editor             
        ).grid(row=4, column=0, columnspan=3, padx=10, pady=10,sticky="NESW")

        # center the window and show it
        center_window(self)
        self.mainloop()

    def load_file(self):
        """
        Open a dialog to pick up a file. After the user has selected a
        file and clicked on the button "open", the filename is copied
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
        Close this window and open the IMSIL input parameter editor 
        with the specified parameters by the user. These are the type
        of the simulation and the path of an existing input file.
        """
        self.destroy()
        ImsilInputParameterEditor(
            type_of_simulation=self.type_sim_combobox_variable.get(),
            input_file_path=self.choose_existing_file_variable.get()
        )


if __name__ == '__main__':
    welcome_window = WelcomeWindow()
