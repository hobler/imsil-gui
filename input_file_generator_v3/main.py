"""
Classes:
    :WelcomeWindow: The main window, where the user can configure the
                    Input Parameter Editor settings.
    :ImsilInputParameterEditor: Based on the four parameters (type of
                    simulation, existing input file, number of regions 
                    and number of atoms) the IMSIL Input Parameter
                    Editor will be opened.
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
from UI.Frames.blanc.blanc_frame import WELCOME as WELCOME

DATABASE_FILE = "parameters.db"


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

def center_window(tk_window):
    """
    Place the given Tk window in the center of the screen.

    :param tk_window: a window of type tk.Tk
    """
    # Hide widget
    tk_window.withdraw()
    # Update "requested size" from geometry manager
    tk_window.update_idletasks()  

    # Get the requested values of the width and height
    window_width = tk_window.winfo_reqwidth()
    window_height = tk_window.winfo_reqheight()

    # Calculate the position of the upper left corner of the window 
    pos_x = int(tk_window.winfo_screenwidth()/2 - window_width/2)
    pos_y = int(tk_window.winfo_screenheight()/2 - window_height/2)

    # Center the window
    tk_window.geometry("+{}+{}".format(pos_x, pos_y))
    # Show widget
    tk_window.deiconify()


class WelcomeWindow(tk.Tk):
    """
    This is the class for the Welcome Window.

    The window contains a header text, a welcome message, a combobox 
    where the user can select a specific type of simulation, an option
    to load an existing IMSIL input file, two parameters, to set the
    number of regions and atoms as well as a button to open the IMSIL
    Input Parameter Editor.

    @type of simulation: based on this option the IMSIL Input Parameter 
    Editor will have different parameters at the beginning of each 
    notebook page. These parameters, so called "basic" parameters, that
    are for this type of simulation common, have to be defined in the 
    database (not yet implemented).
    """
    WINDOW_WIDTH = 470  # Define the window width

    def __init__(self):
        super().__init__()
        self.title("Welcome")
        self.resizable(False, False)
        self.frame = BlancFrame(self, columns=3)

        # Add a header
        self.header_label = tk.Label(self.frame,
                                     font="Helvetica 18 bold",
                                     text="IMSIL input file generator")
        self.header_label.grid(row=0, column=0, columnspan=3, 
                               padx=10, pady=10, sticky="NESW")
        
        # Set the welcome message text
        welcome_text = ("Welcome to the input file generator for IMSIL."
                        " With this tool you can generate an input file"
                        " for IMSIL. You can also edit an existing input"
                        " file by loading it in this window below.")
        # Add the welcome message
        self.welcome_message_label = tk.Label(self.frame,
                                              wraplength=self.WINDOW_WIDTH,
                                              anchor=tk.NW,
                                              text=welcome_text,
                                              justify=tk.LEFT)
        self.welcome_message_label.grid(row=1, column=0, columnspan=3, 
                                        padx=10, pady=10, sticky="NESW")

        # Add a Listbox with elements that can be chosen by the user
        self.type_sim_combobox_variable = tk.StringVar()
        self.choose_type_sim_label = tk.Label(self.frame,
                                              text="Choose type of simulation:")
        self.choose_type_sim_label.grid(row=2, column=0, 
                                        padx=5, pady=0, sticky="NES")
        self.type_sim_combobox = ttk.Combobox(
                self.frame, 
                values=["", "any"],
                textvariable=self.type_sim_combobox_variable)
        self.type_sim_combobox.grid(row=2, column=1, columnspan=2, 
                                    padx=(0, 10), pady=0, sticky="NESW")

        # Add a Label, an Entry to display the file to be loaded and a
        # Button to load an existing file
        self.choose_existing_file_label = tk.Label(
                self.frame,
                text="Load existing input file:")
        self.choose_existing_file_label.grid(row=3, column=0, 
                                             padx=5, pady=0, sticky="NES")
        self.choose_existing_file_variable = tk.StringVar()
        self.choose_existing_file_entry = tk.Entry(
            self.frame, 
            textvariable=self.choose_existing_file_variable)
        self.choose_existing_file_entry.grid(row=3, column=1, 
                                             padx=0, pady=5, sticky="NESW")
        self.choose_existing_file_button = tk.Button(self.frame, 
                                                     text="Load",
                                                     command=self.load_file)
        self.choose_existing_file_button.grid(row=3, column=2, padx=(5, 10), 
                                              pady=4, sticky="NESW")

        # Add a Button to open the IMSIL Input Parameter Editor
        # (The Button has to be added before the callback function)
        self.btn_continue = tk.Button(
            self.frame, 
            text='Open IMSIL Input Parameter Editor',
            padx=10,
            pady=10,
            command=self.open_imsil_input_parameter_editor)
        self.btn_continue.grid(row=5, column=0, columnspan=3,
                               padx=10, pady=10, sticky="NESW")

        # Add a Label, and an Entry for both N_R and N_ATOM within a
        # new Frame, so the positions can be adjusted
        self.var_frame = BlancFrame(self.frame, columns=4, frame_id=WELCOME)
        self.var_frame.grid(row=4, column=0, columnspan=4,
                            padx=(5, 10), pady=4, sticky="NESW")
        self.nr_label = tk.Label(self.var_frame, text="Number of Regions:")
        self.nr_label.grid(row=0, column=0, padx=5, pady=0, sticky="NES")
        self.nr_var = tk.IntVar()
        self.natom_var = tk.IntVar()  # Define before the callback
        self.nr_entry = tk.Entry(self.var_frame,
                                 width=3,
                                 textvariable=self.nr_var,
                                 validate="focusout", 
                                 validatecommand=self.callback_for_button)
        self.nr_entry.grid(row=0, column=1, padx=0, pady=0, sticky="NESW")
        self.natom_label = tk.Label(self.var_frame, text="Number of Atoms:")
        self.natom_label.grid(row=0, column=2, padx=5, pady=0, sticky="NES")
        self.natom_entry = tk.Entry(self.var_frame,
                                    width=3,
                                    textvariable=self.natom_var,
                                    validate="focusout", 
                                    validatecommand=self.callback_for_button)
        self.natom_entry.grid(row=0, column=3, padx=(0, 5), pady=0,
                              sticky="NESW")

        # Center the window and show it
        center_window(self)
        self.mainloop()

    def load_file(self):
        """
        Open the specified file.
        
        Open a dialog to pick a file. After the user has selected a 
        file and clicked on the button "open", the filename is copied
        to the entry to show the user that the file was successfully
        selected.
        TODO: this functionality has not been tested yet
        """
        loaded_file = filedialog.askopenfile(
            initialdir=self.choose_existing_file_variable.get(),
            title="Select IMSIL input file")
        if loaded_file:
            self.choose_existing_file_variable.set(loaded_file.name)
            loaded_file.close()

    def callback_for_button(self):
        """
        Enable/disable the Button for the Imsil Input Parameter Editor.
        
        If both the Number of Regions and the Number of Atoms values 
        are different from 0, enable the Imsil Input Parameter Editor
        Button, otherwise disable it.
        """          
        try:
            if self.natom_var.get() > 0 and self.nr_var.get() > 0:
                self.btn_continue.config(state='active')
            else:
                self.btn_continue.config(state='disabled')
        except Exception:
            # This Exception is triggered for invalid values or empty
            # Entry fields
            self.btn_continue.config(state='disabled')
        
        return True

    def open_imsil_input_parameter_editor(self):
        """
        Open the Imsil Input Parameter Editor.
        
        Close the Welcome Window and open the IMSIL Input Parameter 
        Editor with the parameters (type of simulation, the path of an
        existing input file and nr and natom) specified by the user.
        """        
        # Check if both the Number of Regions and the Number of Atoms 
        # values are different from 0. If yes, enable the Imsil Input 
        # Parameter Editor Button and proceed, otherwise disable it, 
        # show an error message and stay at the welcome window.
        error_title = "Invalid Value"
        error_text = ("Please enter valid values (>0) for both Number "
                      "of Regions and Number of Atoms!")
        try:
            if self.natom_var.get() > 0 and self.nr_var.get() > 0:
                self.btn_continue.config(state='active')
            else:
                tk.messagebox.showerror(title=error_title, message=error_text)
                self.btn_continue.config(state='disabled')
                return True
        except Exception:
            tk.messagebox.showerror(title=error_title, message=error_text)
            self.btn_continue.config(state='disabled')
            return True    
        
        self.destroy() # Close the current Window
        # Open the ImsilInputParameterEditor
        ImsilInputParameterEditor(
            type_of_simulation=self.type_sim_combobox_variable.get(),
            input_file_path=self.choose_existing_file_variable.get(),
            nr=self.nr_var,
            natom=self.natom_var)


class ImsilInputParameterEditor:
    """
    This is the class for the Imsil Input Parameter Editor.
    
    The IMSIL Input Parameter Editor consists of a notebook with tabs,
    where each tab corresponds to a database table.
    """
    def __init__(self, type_of_simulation, input_file_path, nr, natom):
        """
        In the initialization of the IMSIL Input Parameter Editor a 
        notebook is added to the window. The SqliteMaster class is used
        to determine the table names in the database. For each table a
        new tab is added as a DbFrame to the notebook. 

        If a path to an input file is passed, it is read and the 
        parameter values will be placed into the Editor.

        :param type_of_simulation: type of the simulation
        :param input_file_path: path of an existing input file
        :param nr: the number of regions for index variable arrays
        :param natom: the number of atoms for index variable arrays
        """
        if not os.path.isfile(DATABASE_FILE):
            sys.exit(DATABASE_FILE + " does not exist.")
        
        # Create the root window, adjust its title, make it non-
        # resizable and center it
        root = tk.Tk()
        root.title('IMSIL Input Parameter Editor')
        root.resizable(False, False)
        center_window(root)
        
        # Add a loading message (becomes visible after the user presses
        # the button to open the IMSIL Input Parameter Editor in the 
        # Welcome Window)
        label = tk.Label(root, text="Loading data.")
        label.pack()

        # Create the Notebook
        self.nb = ttk.Notebook(root, width=900, height=600)
        
        # Add the necessary tabs
        sqlite_master_table = SqliteMaster(DATABASE_FILE)
        for table_name in sqlite_master_table.get_table_names():
            self.nb.add(DbFrame(parent=self.nb,
                                db_file=DATABASE_FILE,
                                table_name=table_name,
                                type_of_simulation=type_of_simulation,
                                nr=nr,
                                natom=natom,
                                name=table_name),
                        text=table_name)
        
        # Remove the loading message
        label.pack_forget()
        # Place the notebook
        self.nb.grid(row=0, column=0, sticky="NESW")
        
        # If the user has passed the name of an IMSIL input file
        if input_file_path != "":
            # Read IMSIL input file
            input_file = read_existing_input_file(input_file_path)
            if input_file is not None:
                # Go through all params that are defined in the file
                for key in input_file.file.keys():
                    for par_name in input_file.file[key]:
                        if not isinstance(par_name, OrderedDict):
                            # Set parameter value in tab
                            self.set_parameter_value(
                                tab_name=key,
                                parameter_name=par_name,
                                parameter_value=input_file.file[key][par_name])
        
        # Center the window again, since it changed size and show it
        center_window(root)
        root.mainloop()

#    def get_all_parameter_values(self):
#        """
#        Go through all tabs in the notebook and use the ui_data_list 
#        with the stored (default) values of the parameters to get all
#        changes.
#
#        This function can be used later to generate the input file.
#
#        Currently this function is not in use!
#        """
#        for nb_tab in self.nb.tabs():
#            frame = self.nb.nametowidget(nb_tab)
#            if hasattr(frame.scroll_frame, 'ui_data_list'):
#                # frame_ui_data_list = frame.scroll_frame.ui_data_list
#                pass

    def set_parameter_value(self, tab_name, parameter_name, parameter_value):
        """
        Set value of a parameter in the specified tab of the notebook.

        :param tab_name: name of the notebook tab as string
        :param parameter_name: name of the parameter as string
        :param parameter_value: parameter value to be set as a string

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
                    print("There is no parameter with the name " 
                          + parameter_name + " in tab " + tab_name)
            else:
                print("Frame " 
                      + frame 
                      + " does not contain an attribute with the name"
                      + " ui_data_list")
        else:
            print("There is no tab with the name " + tab_name)


if __name__ == '__main__':
    welcome_window = WelcomeWindow()
    