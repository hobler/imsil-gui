"""
Classes:
    :WelcomeWindow: The main window, where the user can configure the
                    Input Parameter Editor settings.
"""
import os, sys
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox, font

from UI.frames.scroll_frame import INFO_WIDTH, INFO_HEIGHT
from UI.frames.region_table_frame import RegionTableFrame
from data_model.element import get_unique_atoms, get_all_elements
from data_model.nml_manager import create_nml, save_nml, load_nml, \
    load_nml_to_parameter_data
from utility import center_window, create_tooltip, create_info_button_text
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
        self.window_width = 500
        font.Font(name="TkCaptionFont", exists=True).config(weight="normal")

        # list of all chemical elements
        self.all_elements = get_all_elements()

        # load structure, names and content of the tables
        self.db_tables = []
        self.load_database_tables()

        # create ParameterData from database tables, this object contains
        # every parameter value and its entries
        self.parameter_data = ParameterData(self.db_tables)

        # set variables and widgets needed across the class

        # ions frame
        self.ion_name_entry_var = None
        self.ion_name_entry = None
        self.ion_energy_entry_var = None
        self.ion_energy_entry = None

        # target frame
        self.target_frame = None
        self.geometry_frame = None
        self.geom_dim_cb_var = tk.StringVar()
        self.geom_dim_cb_var.set("1D")
        self.target_type_cb_var = tk.StringVar()
        self.target_type_cb_var.set("Regions")
        self.target_type_cb = None
        self.region_or_cell_frame = None
        self.cells_entry_var = None

        # control frame
        self.open_param_editor_btn = None
        self.load_btn = None
        self.save_btn = None
        self.save_as_btn = None
        self.check_btn = None
        self.run_btn = None

        # status bar
        self.statusbar_entry_var = tk.StringVar()
        self.statusbar_entry_var.set("No file selected.")
        self.statusbar_entry = None

        # define and load all the frames
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=4, pady=4, sticky="NESW")

        self.load_header_frame(row=0)
        self.load_edit_frames()
        self.load_statusbar(row=4)

        self.enable_editing()

        # temporary string variable that saves the entry value before
        # it was edited, in case the editing gets cancelled
        self.prev_entry_val = ""

        # Center the window and show it
        center_window(self)
        self.mainloop()

    def load_edit_frames(self):
        self.load_ions_frame(row=1)
        self.load_target_frame(row=2)
        self.load_control_frame(row=3)

    def load_header_frame(self, row):
        """
        Define the header consisting of logo and welcome text.

        :param row: Row of main_frame to place header frame into.
        """
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=row, column=0,
                          sticky='we', padx=4, pady=4, ipady=2)

        # logo frame
        logo_frame = ttk.Frame(header_frame, width=150, height=80)
        logo_frame.grid(row=0, column=0, sticky='ns')
        logo_frame.propagate(False)

        # welcome text frame
        welcome_frame = tk.Frame(header_frame)
        welcome_frame.grid(row=0, column=1, sticky='ns', padx=(9, 0))

        # Add logo
        logo = ttk.Label(logo_frame,
                         text="IMSIL", font="Helvetica 30 bold",
                         anchor="center",
                         padding=(0, 8, 0, 0),   # correct vertical alignment
                         background="#ffffff")
        logo.pack(expand=True, fill="both")

        # Set the welcome message text
        welcome_text1 = "Welcome to the IMSIL Input File Generator v3!"
        welcome_text2 = ("With this tool you can load, edit and save input "
                         "files for IMSIL. Start by  loading an existing file "
                         "or create an input file from scratch.")
        # Add the welcome message
        label = ttk.Label(welcome_frame,
                          text=welcome_text1, font="Helvetica 10 bold",
                          wraplength=350, justify='center')
        label.grid(row=0, sticky='ns')
        label = ttk.Label(welcome_frame,
                          text=welcome_text2, font="Helvetica 10",
                          wraplength=350, justify='left')
        label.grid(row=1, sticky='ns')
        welcome_frame.rowconfigure(0, weight=1)
        welcome_frame.rowconfigure(1, weight=1)

    def load_ions_frame(self, row):
        """
        Define the LabelFrame containing the ion properties

        :param row: Row of main_frame to place ions frame into.
        """
        ions_frame = ttk.LabelFrame(self.main_frame, text='Ions', padding=4)
        ions_frame.grid(row=row, column=0,
                        sticky='we', padx=4, pady=4, ipady=2)
        # prepare frame so that name and energy occupy exactly half of the
        # ions_frame horizontally
        ions_frame.columnconfigure(0, uniform='a', weight=1)
        ions_frame.columnconfigure(1, uniform='a', weight=1)

        # ion name
        ion_name_frame = ttk.Frame(ions_frame)
        ion_name_frame.grid(row=0, column=0, sticky='w')

        ion_name_label = ttk.Label(ion_name_frame, text="Name:")
        ion_name_label.grid(row=0, column=0, padx=4)
        ion_name_frame.columnconfigure(0, weight=1)

        ion_name_info_btn = self.create_tooltip_btn(
                ion_name_frame,
                self.parameter_data.get_entry("ions", "NAME"))
        ion_name_info_btn.grid(row=0, column=1)

        self.ion_name_entry_var = tk.StringVar()
        self.ion_name_entry_var.set("<click to change>")
        self.ion_name_entry = ttk.Entry(
                ion_name_frame, width=17,
                textvariable=self.ion_name_entry_var)
        self.ion_name_entry["state"] = "disabled"
        self.ion_name_entry.grid(row=0, column=2, padx=4)
        ion_name_frame.columnconfigure(2, weight=1)

        # ion energy
        ion_energy_frame = ttk.Frame(ions_frame)
        ion_energy_frame.grid(row=0, column=1, sticky='w')

        ion_energy_label = ttk.Label(ion_energy_frame, text="Energy:")
        ion_energy_label.grid(row=0, column=0, sticky='e', padx=4)
        ion_energy_frame.columnconfigure(0, weight=1)

        ion_energy_info_btn = self.create_tooltip_btn(
                ion_energy_frame,
                self.parameter_data.get_entry("ions", "ENERGY"))
        ion_energy_info_btn.grid(row=0, column=1)

        self.ion_energy_entry_var = tk.StringVar()
        self.ion_energy_entry_var.set("<click to change>")
        self.ion_energy_entry = ttk.Entry(
                ion_energy_frame, width=17,
                textvariable=self.ion_energy_entry_var)
        self.ion_energy_entry["state"] = "disabled"
        self.ion_energy_entry.grid(row=0, column=2, sticky='w', padx=4)
        ion_energy_frame.columnconfigure(2, weight=1)

    def load_target_frame(self, row):
        """
        Define the LabelFrame containing the target properties

        :param row: Row of main_frame to place target frame into.
        """
        # target
        self.target_frame = ttk.LabelFrame(self.main_frame, text='Target',
                                           padding=4)
        self.target_frame.grid(row=row, column=0,
                               sticky='we', padx=4, pady=4, ipady=2)

        # prepare frame so that type and - in case of a regions target -
        # geometry occupy exactly half of the target_frame horizontally
        self.target_frame.columnconfigure(0, uniform='a', weight=1)
        self.target_frame.columnconfigure(1, uniform='a', weight=1)

        # target type
        target_type_frame = ttk.Frame(self.target_frame)
        target_type_frame.grid(row=0, column=0, sticky='w')
        target_type_label = ttk.Label(target_type_frame, text="Type:")
        target_type_label.grid(row=0, column=0, padx=4)
        target_type_frame.columnconfigure(0, weight=1)

        self.target_type_cb = ttk.Combobox(
                target_type_frame, width=12,
                textvariable=self.target_type_cb_var)
        self.target_type_cb.grid(row=0, column=1, sticky='w', padx=4)
        self.target_frame.columnconfigure(1, weight=1)
        self.target_type_cb["state"] = 'readonly'
        self.target_type_cb["values"] = ["Regions", "Cells"]
        self.target_type_cb.bind('<<ComboboxSelected>>',
                                 self.on_target_type_cb_change)
        # force the Combobox to steal focus when scrolled
        self.target_type_cb.bind("<MouseWheel>",
                                 lambda event: self.target_type_cb.focus_set())

        if self.target_type_cb_var.get() == 'Regions':
            # geometry
            self.geometry_frame = ttk.Frame(self.target_frame)
            self.geometry_frame.grid(row=0, column=1, sticky='w')

            geometry_label = ttk.Label(self.geometry_frame, text="Geometry:")
            geometry_label.grid(row=0, column=0)

            geom_dim_cb = ttk.Combobox(
                    self.geometry_frame, width=3,
                    textvariable=self.geom_dim_cb_var)
            geom_dim_cb.grid(row=0, column=1, padx=3)
            geom_dim_cb["state"] = "readonly"
            geom_dim_cb["values"] = ["1D", "2D", "3D"]
            geom_dim_cb.bind('<<ComboboxSelected>>',
                             self.on_geom_dim_cb_change)
            # force the Combobox to steal focus when scrolled
            geom_dim_cb.bind("<MouseWheel>",
                             lambda event: geom_dim_cb.focus_set())

            self.load_regions_widgets()
        else:
            if self.geometry_frame is not None:
                self.geometry_frame.destroy()
                self.geometry_frame = None

            self.load_cells_widgets()

    def load_regions_widgets(self):
        """
        Load the region specific widgets for the target.
        """
        if self.region_or_cell_frame is not None:
            self.region_or_cell_frame.destroy()
        self.region_or_cell_frame = RegionTableFrame(
                self.target_frame,
                geometry=self.geom_dim_cb_var.get(),
                parameter_data=self.parameter_data,
                update_atoms=self.update_atoms)
        self.region_or_cell_frame.grid(row=1, column=0, columnspan=2,
                                       sticky="we", pady=(8, 0))

    def load_cells_widgets(self):
        """
        Load the cells specific widgets for the target.
        """
        if self.region_or_cell_frame is not None:
            self.region_or_cell_frame.destroy()
        self.region_or_cell_frame = ttk.Frame(self.target_frame)
        self.region_or_cell_frame.grid(row=1, column=0, columnspan=2,
                                       sticky='we', pady=(8, 0))

        cell_file_label = ttk.Label(self.region_or_cell_frame,
                                    text="Cell File:")
        cell_file_label.grid(row=1, column=0, padx=4)

        cells_info_btn = self.create_tooltip_btn(
            self.region_or_cell_frame,
            self.parameter_data.get_entry("setup", "FILCELL"))
        cells_info_btn.grid(row=1, column=1)

        self.cells_entry_var = tk.StringVar()
        self.cells_entry_var.set("No file selected.")
        cells_entry = tk.Entry(self.region_or_cell_frame,
                               textvariable=self.cells_entry_var)
        cells_entry.grid(row=1, column=2, sticky='we', padx=4, pady=(4, 0))
        self.region_or_cell_frame.columnconfigure(2, weight=1)
        cells_entry["state"] = "readonly"
        cells_entry.bind("<1>", self.on_open_cells_file)

    def load_control_frame(self, row):
        """
        Define the control buttons frame.

        :param row:  Row of main_frame to place control buttons into.
        """
        # control frame
        control_frame = ttk.Frame(self.main_frame, padding=(4, 0))
        control_frame.grid(row=row, column=0, sticky='nw')

        self.open_param_editor_btn = ttk.Button(
                control_frame,
                text="Parameter Editor...",
                command=self.open_imsil_input_parameter_editor,
                state="disabled")
        self.open_param_editor_btn.grid(row=0, column=0,
                                        sticky='we', padx=(0, 1))
        control_frame.columnconfigure(0, weight=2)

        self.load_btn = ttk.Button(
                control_frame,
                text="Load...",
                width=-5,
                command=self.on_open_file,
                state="disabled")
        self.load_btn.grid(row=0, column=1, sticky='we', padx=1)
        control_frame.columnconfigure(1, weight=1)
        # probably not necessary for ttk.Button:
        ## force the button to steal focus when clicked
        #self.load_btn.bind("<1>", lambda event: self.load_btn.focus_set())

        self.save_btn = ttk.Button(
                control_frame,
                text="Save",
                width=-5,
                command=self.on_save,
                state="disabled")
        self.save_btn.grid(row=0, column=2, sticky='we', padx=1)
        control_frame.columnconfigure(2, weight=1)

        self.save_as_btn = ttk.Button(
                control_frame,
                text="Save As...",
                width=-7,
                command=self.on_save_as,
                state="disabled")
        self.save_as_btn.grid(row=0, column=3, sticky='we', padx=1)
        control_frame.columnconfigure(3, weight=1)

        self.check_btn = ttk.Button(
                control_frame,
                text="Check",
                width=-5,
                command=None,
            state="disabled")
        self.check_btn.grid(row=0, column=4, sticky='we', padx=1)
        control_frame.columnconfigure(4, weight=1)

        self.run_btn = ttk.Button(
                control_frame,
                text="Run",
                width=-5,
                command=None,
                state="disabled")
        self.run_btn.grid(row=0, column=5, sticky='we', padx=(1, 0))
        control_frame.columnconfigure(5, weight=1)

    def load_statusbar(self, row):
        self.statusbar_entry = ttk.Entry(self.main_frame,
                                         textvariable=self.statusbar_entry_var)
        self.statusbar_entry.grid(row=row, column=0,
                                  sticky='we', padx=4, pady=4)
        self.main_frame.rowconfigure(row, weight=1)
        self.statusbar_entry["state"] = "disabled"

    def disable_editing(self):
        """Disable the editing entries and buttons."""
        self.open_param_editor_btn["state"] = "disabled"
        self.load_btn["state"] = "disabled"
        self.save_btn["state"] = "disabled"
        self.save_as_btn["state"] = "disabled"
        self.check_btn["state"] = "disabled"
        self.run_btn["state"] = "disabled"

        self.ion_name_entry["state"] = "disabled"
        self.ion_energy_entry["state"] = "disabled"
        self.ion_name_entry_var.set("")
        self.ion_energy_entry_var.set("")

        self.target_type_cb["state"] = "disabled"

    def enable_editing(self):
        """Enable the editing of entries and buttons."""
        self.open_param_editor_btn["state"] = "normal"
        self.save_btn["state"] = "normal"
        self.load_btn["state"] = "normal"
        self.save_as_btn["state"] = "normal"
        self.check_btn["state"] = "disabled"  # not implemented
        self.run_btn["state"] = "disabled"  # not implemented

        self.ion_name_entry["state"] = "normal"
        self.ion_energy_entry["state"] = "normal"
        self.ion_name_entry.bind("<FocusIn>",
                                 self.on_ion_name_entry_focus_in)
        self.ion_name_entry.bind("<FocusOut>",
                                 self.on_ion_name_entry_focus_out)
        self.ion_energy_entry.bind("<FocusIn>",
                                   self.on_ion_energy_entry_focus_in)
        self.ion_energy_entry.bind("<FocusOut>",
                                   self.on_ion_energy_entry_focus_out)

        # load the current ion parameters
        ions = self.parameter_data.get_entry_value("ions", "NAME")
        ion_energy = self.parameter_data.get_entry_value("ions", "ENERGY")
        self.ion_name_entry_var.set(ions)
        self.ion_energy_entry_var.set(ion_energy)

        self.target_type_cb["state"] = "readonly"

    def on_ion_name_entry_focus_in(self, event):
        self.prev_entry_val = self.ion_name_entry_var.get()
        self.ion_name_entry.selection_range(0, 'end')

    def on_ion_name_entry_focus_out(self, event):
        """
        Callback for the on-click event of the Entry-box

        Opens a new simpledialog window that asks the user for the
        new ion name and checks for a valid molecule name.
        """
        # disable another instance of this method from opening
        self.ion_name_entry.unbind("<FocusOut>")

        ion_name = self.ion_name_entry_var.get()

        # while no valid name is given
        while True:
            # check for correct spelling of the molecule
            # TODO: get_unique_atoms does not raise an exception if an invalid
            #  atom name is given after a number, e.g., for 'B2x'.
            unique_atoms = []
            try:
                unique_atoms = get_unique_atoms([ion_name],
                                                self.all_elements)
            except ValueError:
                error = True
            else:
                error = False

            # check if the given string was a molecule name
            if len(unique_atoms) == 0:
                error = True

            if ion_name == "":
                error = False

            if error:
                # info for wrong input
                tk.messagebox.showerror("Invalid Input",
                                        "Invalid Ion Name.")
            else:
                # if name is valid, proceed
                break

            ion_name = simpledialog.askstring(
                    title="Change Ion Name",
                    prompt="New Ion name:",
                    initialvalue=ion_name,
                    parent=self)
            # result of the cancel button
            if ion_name is None:
                # re-enable on-click event
                self.ion_name_entry_var.set(self.prev_entry_val)
                self.ion_name_entry.bind("<FocusOut>",
                                         self.on_ion_name_entry_focus_out)
                return

        # set new name if user didn't cancel
        if ion_name is not None:
            self.ion_name_entry_var.set(ion_name)
            self.parameter_data.set_entry_value("ions", "NAME", ion_name)
            self.update_atoms(change_ion=True)

            # re-enable on-click event
        self.ion_name_entry.bind("<FocusOut>", self.on_ion_name_entry_focus_out)

    def on_ion_energy_entry_focus_in(self, event):
        self.ion_energy_entry.selection_range(0, 'end')

    def on_ion_energy_entry_focus_out(self, event):
        """
        Callback for the focus-out event of the Entry-box.
        """
        ion_energy = self.ion_energy_entry_var.get()
        self.parameter_data.set_entry_value("ions", "ENERGY", ion_energy)
        # TODO: Validate ion energy can be converted to float

    def on_target_type_cb_change(self, value):
        """
        Target Combobox change event.
        Changes Target frame to region or cell view.

        :param value: VirtualEvent passed by the event handler.
        """

        if self.target_type_cb_var.get() == "Regions":
            #self.load_regions_frame()
            self.parameter_data.set_entry_value("setup", "USECELL", "F")
        elif self.target_type_cb_var.get() == "Cells":
            #self.load_cells_frame()
            self.parameter_data.set_entry_value("setup", "USECELL", "T")
        self.load_target_frame(row=2)

    def on_geom_dim_cb_change(self, value):
        self.load_regions_widgets()

    def on_open_cells_file(self, event):
        """
        Opens a File Dialog to open an existing file.
        """
        loaded_file = filedialog.askopenfile(
                initialdir=self.statusbar_entry_var.get(),
                title="Select Cells file")
        if loaded_file:
            self.cells_entry_var.set(loaded_file.name)
            loaded_file.close()
            self.statusbar_entry["state"] = "readonly"

            self.parameter_data.set_entry_value("setup", "FILCELL",
                                                loaded_file.name)

    def open_imsil_input_parameter_editor(self):
        """
        Open the Imsil Input Parameter Editor.
        """

        self.withdraw()  # Hide the current window
        region_names = self.parameter_data.get_materials()

        # Open the ImsilInputParameterEditor
        ImsilInputParameterEditor(
            type_of_simulation=None,
            input_file_path="",
            parameter_data=self.parameter_data,
            region_names=region_names,
            on_close=self.on_close_parameter_editor)

    def on_close_parameter_editor(self, apply=False):
        """
        Callback when closing the parameter editor.

        :param apply: True if the user wants to apply the changes.
        """
        if apply:
            self.parameter_data.readout_parameter_editor()

            usecell = self.parameter_data.get_entry_value("setup", "USECELL")
            if usecell == "T":
                # self.load_cells_frame()
                self.target_type_cb_var.set("Cells")
                filename = self.parameter_data.get_entry_value("setup",
                                                               "FILCELL")
                self.cells_entry_var.set(filename)
            else:
                # self.load_regions_frame()
                self.target_type_cb_var.set("Regions")
            self.load_target_frame(row=2)

            ions = self.parameter_data.get_entry_value("ions", "NAME")
            ion_energy = self.parameter_data.get_entry_value("ions", "ENERGY")
            self.ion_name_entry_var.set(ions)
            self.ion_energy_entry_var.set(ion_energy)

        self.deiconify()

    def on_open_file(self):
        """
        Opens a File Dialog to open an existing file.
        """
        loaded_file = filedialog.askopenfile(
                initialdir=self.statusbar_entry_var.get(),
                title="Select IMSIL input file")
        if loaded_file:
            # set filename in main window
            self.statusbar_entry_var.set(loaded_file.name)
            loaded_file.close()
            self.statusbar_entry["state"] = "readonly"

            # load Namelist and write values to ParameterData
            nml = load_nml(loaded_file.name)
            load_nml_to_parameter_data(self.parameter_data, nml)

            # reload the UI to display everything correctly
            self.load_edit_frames()
            #self.load_regions_frame()
            self.load_target_frame(row=2)
            self.enable_editing()

            # reload the ion parameters, because load_edit_frames clears them
            ions = self.parameter_data.get_entry_value("ions", "NAME")
            ion_energy = self.parameter_data.get_entry_value("ions", "ENERGY")
            self.ion_name_entry_var.set(ions)
            self.ion_energy_entry_var.set(ion_energy)

    def on_save(self):
        filename = self.statusbar_entry_var.get()
        # if no file is selected, try creating a new one
        if filename == "No file selected.":
            self.on_save_as()
        else:
            # create the Namelist and save it
            nml = create_nml(self.parameter_data)
            save_nml(nml, filename)

    def on_save_as(self):
        """
        Opens a File Dialog to create a new file.
        """
        loaded_file = filedialog.asksaveasfile(
                initialdir=self.statusbar_entry_var.get(),
                title="Select IMSIL input file",
                filetypes=[("Input File", ".inp"), ("any", ".*")])
        if loaded_file:
            self.statusbar_entry_var.set(loaded_file.name)

            self.on_save()

            loaded_file.close()
            self.statusbar_entry["state"] = "readonly"

    def create_tooltip_btn(self, parent, parameter_entry):

        short_desc = parameter_entry.get_short_desc()
        par_name = parameter_entry.get_name()
        long_desc = create_info_button_text(parameter_entry)

        info_btn = tk.Button(parent, text="Button",
                             width=INFO_WIDTH, height=INFO_HEIGHT)
        if short_desc is not None:
            create_tooltip(info_btn, info_btn, short_desc)
        photo = tk.PhotoImage(file=os.path.join("pics", "info_sign_1.gif"))
        info_btn.config(image=photo)
        info_btn.image = photo
        info_btn.config(takefocus=False)
        info_btn.config(
                command=lambda: messagebox.showinfo(par_name, long_desc))

        return info_btn

    def update_atoms(self, change_ion=False, change_region=False):
        """
        Recalculates the Atoms for the ion and materials and stores
        the new atoms in the ParameterData.
        """
        # get currently stored data
        materials = self.parameter_data.get_materials()
        nr = len(materials)
        ions = self.parameter_data.get_entry_value("ions", "NAME")
        atoms = self.parameter_data.get_atoms()

        # Empty entries are only allowed when there is no
        # other valid entry in the list
        materials = [x for x in materials if x != '']
        if len(materials) == 0:
            materials = [""]

        # change default value
        if ions.startswith("-"):
            ions = ""

        new_unique_ion_atoms = []
        new_unique_material_atoms = []
        # create new unique atom lists
        try:
            new_unique_ion_atoms = get_unique_atoms([ions],
                                                    self.all_elements)
            new_unique_material_atoms = get_unique_atoms(materials,
                                                         self.all_elements)

        except ValueError:
            tk.messagebox.showerror("Invalid Input",
                                    "Invalid Ion or Material name.")

        # temporary variables, overwritten later
        unique_ion_atoms = []
        unique_material_atoms = []

        ion_atoms_swap = unique_ion_atoms.copy()
        material_atoms_swap = unique_material_atoms.copy()

        if change_ion is False and change_region is False:
            return
        elif change_ion and change_region is False:
            # start with all atoms to calculate the
            # previous unique atoms of the ion
            unique_ion_atoms = atoms
            # unique material atoms stay the same
            unique_material_atoms = new_unique_material_atoms

            # trim material atoms from all atoms to get the
            # previous unique ion atoms
            unique_ion_atoms = unique_ion_atoms[0:-len(unique_material_atoms)]

            # convert atoms to element objects
            try:
                unique_ion_atoms = get_unique_atoms(unique_ion_atoms,
                                                    self.all_elements)
            except ValueError:
                tk.messagebox.showerror("Invalid Input",
                                        "Invalid Ion or Material name.")

            # create changeable copies used to keep track
            # of the order while swapping
            ion_atoms_swap = unique_ion_atoms.copy()
            material_atoms_swap = unique_material_atoms.copy()

            # calculate the atoms that need to be removed from or added to the
            # original parameter_data
            unique_ion_atoms_to_delete = \
                [atom for atom in unique_ion_atoms if
                 atom not in new_unique_ion_atoms]
            unique_ion_atoms_to_add = \
                [atom for atom in new_unique_ion_atoms if
                 atom not in set(unique_ion_atoms)]

            # remove and add atoms
            for atom in reversed(unique_ion_atoms_to_delete):
                index = unique_ion_atoms.index(atom)
                self.parameter_data.remove_atom(index)
                del ion_atoms_swap[index]
            for atom in unique_ion_atoms_to_add:
                self.parameter_data.add_atom_at(new_unique_ion_atoms.index(atom))
                name = atom.name if atom != "" else atom
                ion_atoms_swap.insert(new_unique_ion_atoms.index(atom), name)

        elif change_region and change_ion is False:
            # start with all atoms to calculate the
            # previous unique atoms of the materials
            unique_material_atoms = atoms
            # unique ion atoms stay the same
            unique_ion_atoms = new_unique_ion_atoms

            # trim ion atoms from all atoms to get the
            # previous unique material atoms
            del unique_material_atoms[0:len(unique_ion_atoms)]

            # convert atoms to element objects
            try:
                unique_material_atoms = get_unique_atoms(unique_material_atoms,
                                                         self.all_elements)
            except ValueError:
                tk.messagebox.showerror("Invalid Input",
                                        "Invalid Ion or Material name.")

            # create changeable copies used to keep track
            # of the order while swapping
            ion_atoms_swap = unique_ion_atoms.copy()
            material_atoms_swap = unique_material_atoms.copy()

            # calculate the atoms that need to be removed from or added to the
            # original parameter_data
            unique_material_atoms_to_delete = \
                [atom for atom in unique_material_atoms if
                 atom not in new_unique_material_atoms]
            unique_material_atoms_to_add = \
                [atom for atom in new_unique_material_atoms if
                 atom not in unique_material_atoms]

            for atom in reversed(unique_material_atoms_to_delete):
                index = unique_material_atoms.index(atom)
                self.parameter_data.remove_atom(index + len(new_unique_ion_atoms))
                del material_atoms_swap[index]
            for atom in unique_material_atoms_to_add:
                self.parameter_data.add_atom_at(new_unique_material_atoms.index(atom) +
                                                len(new_unique_ion_atoms))
                name = atom.name if atom != "" else atom
                material_atoms_swap.insert(new_unique_material_atoms.index(atom),
                                           name)

        # used to set the names correctly
        new_unique_atoms = []
        new_unique_atoms.extend(new_unique_ion_atoms)
        new_unique_atoms.extend(new_unique_material_atoms)

        if change_ion:
            # check if the atoms are in order and swap the contents to match the
            # new order of atoms
            if len(new_unique_atoms) == len(ion_atoms_swap) + \
                    len(material_atoms_swap):
                # check and swap ions
                for i in range(len(new_unique_ion_atoms)):
                    # if they aren't in order
                    if new_unique_ion_atoms[i] != ion_atoms_swap[i]:
                        # search the right atom to swap
                        for j in range(i, len(new_unique_ion_atoms)):
                            # if the right atom index is found
                            if ion_atoms_swap[j] == new_unique_ion_atoms[i]:
                                # swap atoms
                                ion_atoms_swap[i], ion_atoms_swap[j] = \
                                    ion_atoms_swap[j], ion_atoms_swap[i]
                                self.parameter_data.swap_atom(i, j)
                                break
            else:
                print("update_atoms(): wrong length at ions change")

        elif change_region:
            # check if the atoms are in order and swap the contents to match the
            # new order of atoms
            if len(new_unique_atoms) == len(ion_atoms_swap) + \
                    len(material_atoms_swap):
                # check and swap materials
                for i in range(len(new_unique_material_atoms)):
                    # if they aren't in order
                    if new_unique_material_atoms[i] != material_atoms_swap[i]:
                        # search the right atom to swap
                        for j in range(i, len(new_unique_material_atoms)):
                            # if the right atom index is found
                            if (material_atoms_swap[j]
                                    == new_unique_material_atoms[i]):
                                # swap atoms
                                (material_atoms_swap[i],
                                 material_atoms_swap[j]) = \
                                    (material_atoms_swap[j],
                                     material_atoms_swap[i])
                                self.parameter_data.swap_atom(
                                    len(ion_atoms_swap) + i,
                                    len(ion_atoms_swap) + j)
                                break
            else:
                print("update_atoms(): wrong length at region change")

        atoms = [x.name if x != "" else x for x in new_unique_atoms]
        for i in range(len(atoms)):
            if len(atoms[i]) == 2:
                atoms[i] = atoms[i][0] + atoms[i][1].lower()
        # add the new atom names in their corresponding IVArray entries
        self.parameter_data.get_entry_value("atoms",
                                            "NAME").values[0] = atoms

        # set correct nr and natom
        natom = len(atoms)
        self.parameter_data.set_entry_value("setup", "NATOM", str(natom))
        self.parameter_data.set_entry_value("setup", "NR", str(nr))

    #def create_control_btn(self, column, text="", width=100, padx=(2, 2),
    #                       command=None, state="normal"):
    #    """
    #    Create a new button in the control frame.
    #    """
    #    frame_btn = tk.Frame(control_frame,
    #                         width=width, height=32)
    #    frame_btn.propagate(False)
    #    frame_btn.grid(row=0, column=column, columnspan=1,
    #                   sticky="NESW", padx=padx, pady=2)
    #    btn = tk.Button(frame_btn, text=text, command=command)
    #    btn.pack(expand=True, fill="both")
    #    btn["state"] = state
    #    # force the button to steal focus when clicked
    #    btn.bind("<1>", lambda event: btn.focus_set())
    #    return btn

    #def create_row_frame(self, row, rows, columns, padx=4, pady=4):
    #    """
    #    Create a new row within this Window with
    #    a given number of rows and columns.
    #    """
    #    row_frame = tk.Frame(self.main_frame,
    #                         width=self.main_frame.winfo_width())
    #    row_frame.grid(row=row, column=0, sticky="NW")#, padx=4, pady=0)
    #    for r in range(rows):
    #        row_frame.rowconfigure(r, weight=1, pad=pady)
    #    for c in range(columns):
    #        row_frame.columnconfigure(c, weight=1, pad=padx)
    #    return row_frame

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

