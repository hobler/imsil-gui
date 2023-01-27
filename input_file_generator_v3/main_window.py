"""
Classes:
    :WelcomeWindow: The main window, where the user can configure the
                    Input Parameter Editor settings.
"""
import os, sys
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox, font

from UI.frames.scroll_frame import INFO_WIDTH, INFO_HEIGHT
from UI.frames.target_frame import TargetFrame
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

        # temporary string variable that saves the entry value before
        # it was edited, in case the editing gets cancelled
        self.prev_entry_val = ""

        # create basic structure with frames
        # main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=4, pady=4, sticky="NESW")
        self.main_frame.rowconfigure(0, weight=1)  # header
        self.main_frame.rowconfigure(1, weight=1)  # ion
        self.main_frame.rowconfigure(2, weight=1)  # target_sel
        self.main_frame.rowconfigure(3, weight=1)  # target
        self.main_frame.rowconfigure(4, weight=1)  # controls
        self.main_frame.rowconfigure(5, weight=1)  # status
        # self.frame.columnconfigure(0, weight=1)
        # self.frame.columnconfigure(1, weight=1)

        self.header_frame = self.create_row_frame(row=0, rows=1, columns=2)
        self.ions_frame = self.create_row_frame(row=1, rows=1, columns=1)
        self.target_select_frame = self.create_row_frame(row=2,
                                                         rows=1, columns=1)
        self.target_frame = self.create_row_frame(row=3, rows=1, columns=1)
        self.button_frame = self.create_row_frame(row=4, rows=1, columns=1)
        self.status_frame = self.create_row_frame(row=5, rows=1, columns=1)

        # header

        # logo frame
        self.logo_frame = tk.Frame(self.header_frame, width=150, height=80)
        self.logo_frame.grid(row=0, column=0, sticky="NS")
        self.logo_frame.propagate(False)

        # title text frame
        self.title_frame = tk.Frame(self.header_frame, width=350, height=80)
        self.title_frame.grid(row=0, column=1, sticky="NS", padx=(6, 0))
        self.title_frame.propagate(False)

        # Add logo
        logo = ttk.Label(self.logo_frame,
                             text="IMSIL",
                             font="Helvetica 30 bold",
                             anchor="center",
                             padding=(0, 8, 0, 0),
                             background="#ffffff")
        logo.pack(expand=True, fill="both")

        # Set the welcome message text
        welcome_text1 = "Welcome to the IMSIL Input File Generator v3!"
        welcome_text2 = ("With this tool you can load, edit and save input "
                         "files for IMSIL. Start by  loading an existing file "
                         "or create an input file from scratch.")
        # Add the welcome message
        label = tk.Label(self.title_frame,
                          font="Helvetica 10 bold",
                          wraplength=350,
                          #anchor='center',
                          text=welcome_text1,
                          justify='center')
        label.grid(row=0, sticky='ns')
        label = ttk.Label(self.title_frame,
                          font="Helvetica 10",
                          wraplength=350,
                          #anchor='center',
                          text=welcome_text2,
                          justify='left')
        label.grid(row=1, sticky='ns')
        self.title_frame.grid_rowconfigure(0, weight=1)
        self.title_frame.grid_rowconfigure(1, weight=1)

        # ions

        # will be loaded in load_edit_frames()
        self.ions_label_frame = None
        self.ions_label = None
        self.ion_name_label_frame = None
        self.ion_name_label = None
        self.ion_name_entry_var = None
        self.ion_name_entry_frame = None
        self.ion_name_entry = None
        self.ion_name_info_btn = None
        self.ion_energy_label_frame = None
        self.ion_energy_label = None
        self.ion_energy_entry_var = None
        self.ion_energy_entry_frame = None
        self.ion_energy_entry = None
        self.ion_energy_info_btn = None

        # target select
        self.label_target_frame = None
        self.target_label = None
        self.target_select_cb_var = None
        self.target_select_cb_frame = None
        self.target_select_cb = None

        # region frame
        self.region_frame = None
        self.load_cells_btn = None
        self.cells_entry_var = None

        # self.frame_region.pack(expand=True, fill="both")
        # self.frame_region.rowconfigure(0, weight=1)

        # cells
        self.label_cells_frame = None
        self.cells_label = None

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

        self.statusbar_frame = tk.Frame(self.status_frame,
                                        width=self.window_width-8,
                                        height=32)
        self.statusbar_frame.propagate(False)
        self.statusbar_frame.grid(row=0, column=0,
                                  sticky="NESW", padx=6, pady=2)
        self.statusbar_entry = tk.Entry(self.statusbar_frame,
                                        textvariable=self.statusbar_entry_var)
        self.statusbar_entry.pack(expand=True, fill="both")
        self.statusbar_entry["state"] = "disabled"

        # load structure, names and content of the tables
        self.db_tables = []
        self.load_database_tables()

        # create ParameterData from database tables, this object contains
        # every parameter value and its entries
        self.parameter_data = ParameterData(self.db_tables)

        # load everything at startup
        self.load_edit_frames()
        self.load_region_frame()
        self.enable_editing()

        # Center the window and show it
        center_window(self)
        self.mainloop()

    def disable_editing(self):
        """ Disables the editing entries and buttons """
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

        self.target_select_cb["state"] = "disabled"

    def enable_editing(self):
        """ Enables the editing entries and buttons """
        self.open_param_editor_btn["state"] = "normal"
        self.save_btn["state"] = "normal"
        self.load_btn["state"] = "normal"
        self.save_as_btn["state"] = "normal"
        self.check_btn["state"] = "disabled"  # not implemented
        self.run_btn["state"] = "disabled"  # not implemented

        self.ion_name_entry["state"] = "normal"
        self.ion_energy_entry["state"] = "normal"
        self.ion_name_entry.bind("<FocusOut>",
                                 self.on_entry_ion_focus_out)
        self.ion_name_entry.bind("<FocusIn>",
                                 self.on_entry_ion_focus_in)
        self.ion_energy_entry.bind("<FocusOut>",
                                   self.on_entry_ion_energy_focus_out)

        # load the current ion parameters
        ions = self.parameter_data.get_entry_value("ions", "NAME")
        ion_energy = self.parameter_data.get_entry_value("ions", "ENERGY")
        self.ion_name_entry_var.set(ions)
        self.ion_energy_entry_var.set(ion_energy)

        self.target_select_cb["state"] = "readonly"

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

    def on_save(self):
        filename = self.statusbar_entry_var.get()
        # if no file is selected, try creating a new one
        if filename == "No file selected.":
            self.on_save_as()
        else:
            # create the Namelist and save it
            nml = create_nml(self.parameter_data)
            save_nml(nml, filename)

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
            self.load_region_frame()
            self.enable_editing()

            # reload the ion parameters, because load_edit_frames clears them
            ions = self.parameter_data.get_entry_value("ions", "NAME")
            ion_energy = self.parameter_data.get_entry_value("ions", "ENERGY")
            self.ion_name_entry_var.set(ions)
            self.ion_energy_entry_var.set(ion_energy)

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

    def load_edit_frames(self):

        # ions

        self.ions_label_frame = tk.Frame(self.ions_frame, width=30, height=32)
        self.ions_label_frame.grid(row=0, column=0,
                                   sticky="NW", padx=(9, 6), pady=0)
        self.ions_label_frame.propagate(False)

        self.ions_label = tk.Label(self.ions_label_frame, text="Ions:")
        self.ions_label.pack(expand=True, fill="both")

        self.ion_name_label_frame = tk.Frame(self.ions_frame,
                                             width=115, height=32)
        self.ion_name_label_frame.grid(row=0, column=1, sticky="NW",
                                       padx=0, pady=0)
        self.ion_name_label_frame.propagate(False)

        self.ion_name_label = tk.Label(self.ion_name_label_frame,
                                       anchor=tk.E, text="Chem. Name:")
        self.ion_name_label.pack(expand=True, fill="both")

        self.ion_name_entry_var = tk.StringVar()
        self.ion_name_entry_var.set("<click to change>")
        self.ion_name_entry_frame = tk.Frame(self.ions_frame,
                                             width=110, height=24)
        self.ion_name_entry_frame.grid(row=0, column=3, sticky="NW",
                                       padx=(4, 0), pady=(4, 0))
        self.ion_name_entry_frame.propagate(False)
        self.ion_name_entry = tk.Entry(self.ion_name_entry_frame,
                                       textvariable=self.ion_name_entry_var)
        self.ion_name_entry.pack(expand=True, fill="both")
        self.ion_name_entry["state"] = "disabled"
        self.ion_name_info_btn = self.create_tooltip_btn(
            self.ions_frame,
            self.parameter_data.get_entry("ions", "NAME"))
        self.ion_name_info_btn.grid(row=0, column=2, sticky="NW",
                                    padx=(0, 0), pady=(7, 0))

        self.ion_energy_label_frame = tk.Frame(self.ions_frame,
                                               width=80, height=32)
        self.ion_energy_label_frame.grid(row=0, column=4, sticky="NW",
                                         padx=0, pady=0)
        self.ion_energy_label_frame.propagate(False)

        self.ion_energy_label = tk.Label(self.ion_energy_label_frame,
                                         anchor=tk.E,
                                         text="Energy:",
                                         justify=tk.LEFT)
        self.ion_energy_label.pack(expand=True, fill="both")

        self.ion_energy_entry_var = tk.StringVar()
        self.ion_energy_entry_var.set("<click to change>")
        self.ion_energy_entry_frame = tk.Frame(self.ions_frame,
                                               width=110, height=24)
        self.ion_energy_entry_frame.grid(row=0, column=6, sticky="NW",
                                         padx=(4, 0), pady=(4, 0))
        self.ion_energy_entry_frame.propagate(False)
        self.ion_energy_entry = tk.Entry(
            self.ion_energy_entry_frame,
            textvariable=self.ion_energy_entry_var)
        self.ion_energy_entry.pack(expand=True, fill="both")
        self.ion_energy_entry["state"] = "disabled"
        self.ion_energy_info_btn = self.create_tooltip_btn(
            self.ions_frame,
            self.parameter_data.get_entry("ions", "ENERGY"))
        self.ion_energy_info_btn.grid(row=0, column=5, sticky="NW",
                                      padx=(0, 0), pady=(7, 0))

        # target select

        self.label_target_frame = tk.Frame(self.target_select_frame,
                                           width=50, height=32)
        self.label_target_frame.grid(row=0, column=0, sticky="NW",
                                     padx=9, pady=0)
        self.label_target_frame.propagate(False)

        self.target_label = tk.Label(self.label_target_frame,
                                     anchor=tk.E,
                                     text="Target:",
                                     justify=tk.LEFT)
        self.target_label.pack(expand=True, fill="both")

        self.target_select_cb_var = tk.StringVar()
        self.target_select_cb_var.set("Regions")
        self.target_select_cb_frame = tk.Frame(self.target_select_frame,
                                               width=100, height=24)
        self.target_select_cb_frame.grid(row=0, column=1, sticky="NW",
                                         padx=(4, 0), pady=(4, 0))
        self.target_select_cb_frame.propagate(False)
        self.target_select_cb = ttk.Combobox(
            self.target_select_cb_frame,
            textvariable=self.target_select_cb_var)
        self.target_select_cb.pack(expand=True, fill="both")
        self.target_select_cb["state"] = "disabled"
        self.target_select_cb["values"] = ["Regions", "Cells"]
        self.target_select_cb.bind('<<ComboboxSelected>>', self.cb_change)
        # force the Combobox to steal focus when scrolled
        self.target_select_cb.bind("<MouseWheel>",
                                   lambda event: self.target_select_cb.focus_set())

        # control frame

        self.open_param_editor_btn = self.create_control_btn(
            column=0,
            text="Parameter Editor...",
            width=150, padx=(6, 2),
            command=self.open_imsil_input_parameter_editor,
            state="disabled")
        self.load_btn = self.create_control_btn(column=1, text="Load...",
                                                width=53, padx=(11, 2),
                                                command=self.on_open_file,
                                                state="disabled")
        self.save_btn = self.create_control_btn(column=2, text="Save",
                                                width=53, padx=(2, 2),
                                                command=self.on_save,
                                                state="disabled")
        self.save_as_btn = self.create_control_btn(column=3, text="Save As...",
                                                   width=70, padx=(2, 2),
                                                   command=self.on_save_as,
                                                   state="disabled")
        self.check_btn = self.create_control_btn(column=4, text="Check",
                                                 width=60, padx=(2, 2),
                                                 command=None, state="disabled")
        self.run_btn = self.create_control_btn(column=5, text="Run",
                                               width=80, padx=(2, 2),
                                               command=None, state="disabled")

    def load_region_frame(self):
        """
        Load the Region view for the Target
        """
        if self.region_frame is not None:
            self.region_frame.destroy()
        self.region_frame = TargetFrame(self.target_frame, text="Regions",
                                        parameter_data=self.parameter_data,
                                        update_atoms=self.update_atoms)
        self.region_frame.grid(row=0, column=0, sticky="NW",
                               padx=6, pady=(0, 3))

    def load_cells_frame(self):
        """
        Load the Cells view for the Target
        """
        if self.region_frame is not None:
            self.region_frame.destroy()
        self.region_frame = tk.Frame(self.target_frame)
        self.region_frame.grid(row=0, column=0, sticky="NW",
                               padx=6, pady=(0, 3))

        self.label_cells_frame = tk.Frame(self.region_frame,
                                          width=70, height=32)
        self.label_cells_frame.grid(row=0, column=0, sticky="NESW",
                                    padx=(0, 2), pady=2)
        self.label_cells_frame.propagate(False)

        self.cells_label = tk.Label(self.label_cells_frame,
                                    anchor=tk.E,
                                    text="Cell File:",
                                    justify=tk.LEFT)
        self.cells_label.pack(expand=True, fill="both")

        cells_info_btn = self.create_tooltip_btn(
            self.region_frame,
            self.parameter_data.get_entry("setup", "FILCELL"))
        cells_info_btn.grid(row=0, column=1, sticky="NW",
                            padx=(0, 0), pady=(9, 0))

        self.cells_entry_var = tk.StringVar()
        self.cells_entry_var.set("No file selected.")
        cells_entry_frame = tk.Frame(self.region_frame,
                                     width=self.window_width-92, height=32)
        cells_entry_frame.propagate(False)
        cells_entry_frame.grid(row=0, column=2,
                               sticky="NESW", padx=2, pady=2)
        cells_entry = tk.Entry(cells_entry_frame,
                               textvariable=self.cells_entry_var)
        cells_entry.pack(expand=True, fill="both")
        cells_entry["state"] = "readonly"
        cells_entry.bind("<1>", self.on_open_cells_file)

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

    def cb_change(self, value):
        """
        Target Combobox change event.
        Changes Target frame to region or cell view.

        :param value: VirtualEvent passed by the event handler.
        """

        if self.target_select_cb_var.get() == "Regions":
            self.load_region_frame()
            self.parameter_data.set_entry_value("setup", "USECELL", "F")
        elif self.target_select_cb_var.get() == "Cells":
            self.load_cells_frame()
            self.parameter_data.set_entry_value("setup", "USECELL", "T")

    def on_entry_ion_focus_in(self, event):
        self.prev_entry_val = self.ion_name_entry_var.get()

    def on_entry_ion_focus_out(self, event):
        """
        Callback for the on-click event of the Entry-box

        Opens a new simpledialog window that asks the user for the
        new ion name and checks for a valid molecule name.
        """
        # disable another instance of this method from opening
        self.ion_name_entry.unbind("<FocusOut>")

        # initial value for the simpledialog
        initial = self.ion_name_entry_var.get()

        new_name = initial
        first = True

        # while no valid name is given
        while True:
            if not first:
                new_name = simpledialog.askstring(
                    title="Change Ion Name",
                    prompt="New Ion name:",
                    initialvalue=initial,
                    parent=self)
            first = False
            # result of the cancel button
            if new_name is None:
                # re-enable on-click event
                self.ion_name_entry_var.set(self.prev_entry_val)
                self.ion_name_entry.bind("<FocusOut>",
                                         self.on_entry_ion_focus_out)
                return
            initial = new_name

            # check for correct spelling of the molecule
            unique_atoms = []
            try:
                unique_atoms = get_unique_atoms([new_name],
                                                self.all_elements)
            except ValueError:
                error = True
            else:
                error = False
            # check if the given string was a molecule name
            if len(unique_atoms) == 0:
                error = True

            if new_name == "":
                error = False

            if error:
                # info for wrong input
                tk.messagebox.showerror("Invalid Input",
                                        "Invalid Ion Name.")
            else:
                # if name is valid, proceed
                break

        # set new name if user didn't cancel
        if new_name is not None:
            self.ion_name_entry_var.set(new_name)
            self.parameter_data.set_entry_value("ions", "NAME", new_name)
            self.update_atoms(change_ion=True)

            # re-enable on-click event
        self.ion_name_entry.bind("<FocusOut>", self.on_entry_ion_focus_out)

    def on_entry_ion_energy_focus_out(self, event):
        """
        Callback for the focus-out event of the Entry-box.
        """

        new_name = self.ion_energy_entry_var.get()
        self.parameter_data.set_entry_value("ions", "ENERGY", new_name)

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

    def create_control_btn(self, column, text="", width=100, padx=(2, 2),
                           command=None, state="normal"):
        """
        Create a new button in the control frame.
        """
        frame_btn = tk.Frame(self.button_frame,
                             width=width, height=32)
        frame_btn.propagate(False)
        frame_btn.grid(row=0, column=column, columnspan=1,
                       sticky="NESW", padx=padx, pady=2)
        btn = tk.Button(frame_btn, text=text, command=command)
        btn.pack(expand=True, fill="both")
        btn["state"] = state
        # force the button to steal focus when clicked
        btn.bind("<1>", lambda event: btn.focus_set())
        return btn

    def create_row_frame(self, row, rows, columns, padx=4, pady=4):
        """
        Create a new row within this Window with
        a given number of rows and columns.
        """
        row_frame = tk.Frame(self.main_frame,
                             width=self.main_frame.winfo_width())
        row_frame.grid(row=row, column=0, sticky="NW")#, padx=4, pady=0)
        for r in range(rows):
            row_frame.rowconfigure(r, weight=1, pad=pady)
        for c in range(columns):
            row_frame.columnconfigure(c, weight=1, pad=padx)
        return row_frame

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
        """

        self.withdraw()     # Hide the current window
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
                self.load_cells_frame()
                self.target_select_cb_var.set("Cells")
                filename = self.parameter_data.get_entry_value("setup",
                                                               "FILCELL")
                self.cells_entry_var.set(filename)
            else:
                self.load_region_frame()
                self.target_select_cb_var.set("Regions")

            ions = self.parameter_data.get_entry_value("ions", "NAME")
            ion_energy = self.parameter_data.get_entry_value("ions", "ENERGY")
            self.ion_name_entry_var.set(ions)
            self.ion_energy_entry_var.set(ion_energy)

        self.deiconify()
