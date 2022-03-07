"""
Classes:
    :WelcomeWindow: The main window, where the user can configure the
                    Input Parameter Editor settings.
"""
import os, sys
import tkinter as tk
from tkinter import ttk, filedialog

from data_model.iv_data import IVData
from edit_window import EditWindow
from utility import center_window
from parameter_editor_window import ImsilInputParameterEditor
from data_model.read_sqlite import get_database_table_names, DatabaseTable
from data_model.parameter_data import ParameterData

DATABASE_FILE = "parameters.db"


class MainWindow(tk.Tk):
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

    def __init__(self):
        super().__init__()
        self.title("IMSIL GUI")
        self.resizable(False, False)
        # self.minsize(900, 500)

        # create basic structure with frames
        # main frame
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="NESW")
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # logo frame
        self.frame_logo = tk.Frame(self.frame, width=200+8, height=100)
        self.frame_logo.grid(row=0, column=0, sticky="NW",
                             padx=(6, 0), pady=(9, 3))
        self.frame_logo.propagate(False)

        # title text frame
        self.frame_title = tk.Frame(self.frame, width=478, height=100)
        self.frame_title.grid(row=0, column=1, sticky="NW",
                              padx=(6, 0), pady=(9, 3))
        self.frame_title.propagate(False)

        # control frame
        self.frame_control = tk.Frame(self.frame)
        self.frame_control.grid(row=1, column=0, sticky="NW",
                                padx=(6, 0), pady=(6, 0))
        self.frame_control.rowconfigure(0, weight=1)
        self.frame_control.rowconfigure(1, weight=1)
        self.frame_control.rowconfigure(2, weight=1)
        self.frame_control.rowconfigure(3, weight=1)
        self.frame_control.rowconfigure(4, weight=1)
        self.frame_control.columnconfigure(0, weight=1)
        self.frame_control.columnconfigure(1, weight=1)

        # region frame
        self.frame_region = tk.LabelFrame(self.frame, text="Regions",
                                          width=480, height=6*32+5*4+3+6)
        self.frame_region.grid(row=1, column=1, sticky="NW",
                               padx=6, pady=(0, 3))
        self.frame_region.propagate(False)

        # simulation frame
        self.frame_simulation = tk.LabelFrame(self.frame, text="Simulation",
                                              width=6+200+4+480+4, height=176)
        self.frame_simulation.grid(row=2, column=0, columnspan=2, sticky="NW",
                                   padx=6, pady=(0, 6))
        self.frame_simulation.propagate(False)

        # Add a logo (title for now)
        self.header_label = tk.Label(self.frame_logo,
                                     font="Helvetica 30 bold",
                                     text="IMSIL",
                                     bg="#ffffff")
        self.header_label.pack(expand=True, fill="both")

        # Set the welcome message text
        welcome_text = ("Welcome to the IMSIL Input File Generator v3!\n"
                        "With this tool you can load, edit and save input "
                        "files for IMSIL.\n"
                        "Start by  loading an existing file or create a file "
                        "from scratch with the 'Region Editor...'. \n"
                        "Parameters can then be edited in the "
                        "'Parameter Editor...'. \n"
                        "The 'Regions' tab gives an overview of the currently "
                        "used region parameters.\n"
                        "'Geometry Editor...' and the 'Simulation' section "
                        "are currently not implemented.")
        # Add the welcome message
        self.welcome_message_label = tk.Label(self.frame_title,
                                              font="Helvetica 9",
                                              wraplength=465,
                                              anchor=tk.W,
                                              text=welcome_text,
                                              justify=tk.LEFT)
        self.welcome_message_label.pack(expand=True, fill="both")

        # add control buttons
        self.frame_btn_load, self.btn_load = self.create_control_btn(
            row=0, column=0, text="Load Existing Input File...",
            col_span=2, command=self.load_file, state="normal")

        # loaded file label
        self.load_existing_file_variable = tk.StringVar()
        self.load_existing_file_variable.set("No file selected.")
        self.frame_label_load = tk.Frame(self.frame_control,
                                         width=200, height=32)
        self.frame_label_load.propagate(False)
        self.frame_label_load.grid(row=1, column=0, columnspan=2,
                                   sticky="NESW", padx=2, pady=2)
        self.label_load = tk.Entry(self.frame_label_load,
                                   textvariable=self.load_existing_file_variable)
        self.label_load.pack(expand=True, fill="both")
        self.label_load["state"] = "disabled"

        self.frame_btn_save, self.btn_save = self.create_control_btn(
            row=2, column=0, text="Save",
            col_span=1, command=None, state="disabled")
        self.frame_btn_save_as, self.btn_save_as = self.create_control_btn(
            row=2, column=1, text="Save As...",
            col_span=1, command=None, state="disabled")
        self.frame_btn_edit_rgn, self.btn_edit_rgn = self.create_control_btn(
            row=3, column=0, text="Region Editor...",
            col_span=2, command=self.open_region_editor, state="normal")
        self.frame_btn_edit_param, self.btn_edit_param = self.create_control_btn(
            row=4, column=0, text="Parameter Editor...", col_span=2,
            command=self.open_imsil_input_parameter_editor, state="normal")
        self.frame_btn_edit_geom, self.btn_edit_geom = self.create_control_btn(
            row=5, column=0, text="Geometry Editor...",
            col_span=2, command=None, state="disabled")

        # load structure, names and content of the tables
        self.db_tables = []
        self.load_database_tables()

        # create ParameterData from database tables, this object contains
        # every parameter value and its entries
        self.parameter_data = ParameterData(self.db_tables)

        # Center the window and show it
        center_window(self)
        self.mainloop()

    def create_control_btn(self, row, column, text="", col_span=1,
                           command=None, state="normal"):
        frame_btn = tk.Frame(self.frame_control,
                             width=100 * col_span, height=32)
        frame_btn.propagate(False)
        frame_btn.grid(row=row, column=column, columnspan=col_span,
                       sticky="NESW", padx=2, pady=2)
        btn = tk.Button(frame_btn, text=text, command=command)
        btn.pack(expand=True, fill="both")
        btn["state"] = state
        return frame_btn, btn

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
            self.label_load["state"] = "readonly"

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

    def open_region_editor(self):
        """
        Open the Region Editor to edit the Ion an Materials. (edit_window.py)

        """

        iv_dict = self.parameter_data.to_iv_dict()

        ions = self.parameter_data.get_entry("ions", "NAME").get_value()
        materials = self.parameter_data.get_entry("material", "NAME").get_value()

        # first time opening
        if materials == "-- (obligatory)":
            materials = [""]
        else:
            # convert from ivdata to simple list of strings
            materials = materials.to_list()

        # hide this window
        self.withdraw()
        # open edit window with callback function to return new ivdata
        edit_window = EditWindow(ions, materials, iv_dict,
                                 self.on_close_region_editor)

    def on_close_region_editor(self, change=False, iv_dict=None,
                                      new_ion=None, natom=0, nr=0,
                                      atoms=None, regions=None):
        """
                Callback function. Gets called when the EditWindow closes.

                :param change: True, if the arrays should get updated.
                :param iv_dict: The data structure containing the entries (IVDict object)
                :param new_ion: New ion name
                :param natom: new number of atoms
                :param nr: new number of regions
                :param atoms: names of the atoms
                :param regions: names of the regions
                """
        # re-enable this window
        self.deiconify()
        # if something has changed
        if change:
            # load values to parameter_data
            self.parameter_data.load_from_iv_dict(iv_dict)
            # set correct ion name
            # (material and atom names are already
            # named in edit_window.py on_btn_ok())
            self.parameter_data.set_entry_value("ions", "NAME", new_ion)
            # set new NR and NATOM
            self.parameter_data.set_entry_value("setup", "NR", nr)
            self.parameter_data.set_entry_value("setup", "NATOM", natom)

    def open_imsil_input_parameter_editor(self):
        """
        Open the Imsil Input Parameter Editor.

        Close the Welcome Window and open the IMSIL Input Parameter Editor
        with the parameters (type of simulation, the path of an existing
        input file and nr and natom) specified by the user.
        """

        self.destroy()  # Close the current Window

        # Open the ImsilInputParameterEditor
        ImsilInputParameterEditor(
            type_of_simulation=None,
            input_file_path=self.load_existing_file_variable.get(),
            nr=self.parameter_data.get_nr(),
            natom=self.parameter_data.get_natom(),
            parameter_data=self.parameter_data)
