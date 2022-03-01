"""
Classes:
    :WelcomeWindow: The main window, where the user can configure the
                    Input Parameter Editor settings.
"""
import os, sys
import tkinter as tk
from tkinter import ttk, filedialog

from UI.frames.blanc_frame import BlancFrame, WELCOME
from utility import center_window
from parameter_editor_window import ImsilInputParameterEditor
from data_model.read_sqlite import get_database_table_names, DatabaseTable
from data_model.parameter_data import ParameterData

DATABASE_FILE = "parameters.db"


class WelcomeWindow(tk.Tk):
    """
    This is the class for the Welcome Window.

    The window contains a header text, a welcome message, a combobox
    where the user can select a specific type of simulation, an option
    to load an existing IMSIL input file, two parameters, to set the
    number of regions and atoms as well as a button to open the IMSIL
    Input Parameter Editor.

    @type of simulation: based on this option the IMSIL Input Parameter
    Editor will highlight different parameters relevant to this type of
    simulation. These parameters have to be defined in the database (not yet
    implemented).
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
                        " for IMSIL. Start with either loading an "
                        "existing input file or by specifying the number of "
                        "regions and records directly. By pressing the "
                        "'Open IMSIL Input Parameter Editor' button you can "
                        "edit all input parameter values.")
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
        self.type_sim_combobox_variable.set("not yet implemented")
        self.type_sim_combobox.config(state='disabled')
        self.type_sim_combobox.grid(row=2, column=1, columnspan=2,
                                    padx=(0, 10), pady=0, sticky="NESW")

        # Add a Label, an Entry to display the file to be loaded and a
        # Button to load an existing file
        self.load_existing_file_label = tk.Label(
            self.frame,
            text="Load existing input file:")
        self.load_existing_file_label.grid(row=3, column=0,
                                           padx=5, pady=0, sticky="NES")
        self.load_existing_file_variable = tk.StringVar()
        self.load_existing_file_entry = tk.Entry(
            self.frame,
            textvariable=self.load_existing_file_variable)
        self.load_existing_file_entry.grid(row=3, column=1,
                                           padx=0, pady=5, sticky="NESW")
        self.load_existing_file_button = tk.Button(self.frame,
                                                   text="Load",
                                                   command=self.load_file)
        self.load_existing_file_button.grid(row=3, column=2, padx=(5, 10),
                                            pady=4, sticky="NESW")

        # Add a Button to open the IMSIL Input Parameter Editor
        # (The Button has to be added before the callback function)
        self.edit_button = tk.Button(
            self.frame,
            text='Open IMSIL Input Parameter Editor',
            padx=10,
            pady=10,
            command=self.open_imsil_input_parameter_editor)
        self.edit_button.grid(row=5, column=0, columnspan=3,
                              padx=10, pady=10, sticky="NESW")

        # Add a Label, and an Entry for both NR and NATOM within a
        # new Frame, so the positions can be adjusted
        self.var_frame = BlancFrame(self.frame, columns=4, frame_id=WELCOME)
        self.var_frame.grid(row=4, column=0, columnspan=4,
                            padx=(5, 10), pady=4, sticky="NESW")
        self.nr_label = tk.Label(self.var_frame, text="Number of Regions:")
        self.nr_label.grid(row=0, column=0, padx=5, pady=0, sticky="NES")
        self.nr_var = tk.IntVar()
        self.nr_var.set(1)
        self.natom_var = tk.IntVar()  # Define before the callback
        self.natom_var.set(2)
        self.nr_entry = tk.Entry(self.var_frame,
                                 width=3,
                                 textvariable=self.nr_var,
                                 validate="focusout",
                                 validatecommand=self.toggle_edit_button_active)
        self.nr_entry.grid(row=0, column=1, padx=0, pady=0, sticky="NESW")
        self.natom_label = tk.Label(self.var_frame, text="Number of Atoms:")
        self.natom_label.grid(row=0, column=2, padx=5, pady=0, sticky="NES")
        self.natom_entry = tk.Entry(self.var_frame,
                                    width=3,
                                    textvariable=self.natom_var,
                                    validate="focusout",
                                    validatecommand=self.toggle_edit_button_active)
        self.natom_entry.grid(row=0, column=3, padx=(0, 5), pady=0,
                              sticky="NESW")

        # load structure, names and content of the tabs
        self.db_tables = []
        self.load_database_tables()

        # create ParameterData from database tables, this object contains
        # every parameter value and its entries
        self.parameter_data = ParameterData(self.db_tables)

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
                initialdir=self.load_existing_file_variable.get(),
                title="Select IMSIL input file")
        if loaded_file:
            self.load_existing_file_variable.set(loaded_file.name)
            loaded_file.close()

    def toggle_edit_button_active(self):
        """
        Enable/disable the Button for the Imsil Input Parameter Editor.

        If both the Number of Regions and the Number of Atoms values
        are different from 0, enable the Imsil Input Parameter Editor
        Button, otherwise disable it.
        """
        try:
            if self.natom_var.get() > 0 and self.nr_var.get() > 0:
                self.edit_button.config(state='active')
            else:
                self.edit_button.config(state='disabled')
        except Exception:
            # This Exception is triggered for invalid values or empty
            # Entry fields
            self.edit_button.config(state='disabled')

        return True

    def load_database_tables(self):
        """
        Loads the data for each tab from the Database
        and fills the db_tables list.

        Exits the program if the database file was not found.
        """

        # clear the list if it already contains data
        if len(self.db_tables) > 0:
            self.db_tables.clear()

        # load database tables to create and populate the tabs
        if not os.path.isfile(DATABASE_FILE):
            sys.exit(DATABASE_FILE + " does not exist.")

        # get database table for each tab
        for table_name in get_database_table_names(DATABASE_FILE):
            db_table = DatabaseTable(DATABASE_FILE, table_name)
            db_table.regroup()
            self.db_tables.append(db_table)

    def open_imsil_input_parameter_editor(self):
        """
        Open the Imsil Input Parameter Editor.

        Close the Welcome Window and open the IMSIL Input Parameter Editor
        with the parameters (type of simulation, the path of an existing
        input file and nr and natom) specified by the user.
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
                self.edit_button.config(state='active')
            else:
                tk.messagebox.showerror(title=error_title, message=error_text)
                self.edit_button.config(state='disabled')
                return True
        except Exception:
            tk.messagebox.showerror(title=error_title, message=error_text)
            self.edit_button.config(state='disabled')
            return True

        self.destroy()  # Close the current Window

        # TODO: for reading in files:
        #   read values in this class and pass them to
        #   the ImsilInputParameterEditor

        # Open the ImsilInputParameterEditor
        ImsilInputParameterEditor(
            type_of_simulation=self.type_sim_combobox_variable.get(),
            input_file_path=self.load_existing_file_variable.get(),
            nr=self.parameter_data.get_nr(),
            natom=self.parameter_data.get_natom(),
            parameter_data=self.parameter_data)
