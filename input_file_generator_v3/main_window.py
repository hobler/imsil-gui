"""
Classes:
    :WelcomeWindow: The main window, where the user can configure the
                    Input Parameter Editor settings.
"""
import os, sys
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog

from UI.frames.target_frame import TargetFrame
from data_model.element import get_unique_atoms, get_all_elements
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

        self.window_width = 500

        self.all_elements = get_all_elements()

        # create basic structure with frames
        # main frame
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="NESW")
        self.frame.rowconfigure(0, weight=1)  # top
        self.frame.rowconfigure(1, weight=1)  # file
        self.frame.rowconfigure(2, weight=1)  # ion
        self.frame.rowconfigure(3, weight=1)  # target_sel
        self.frame.rowconfigure(4, weight=1)  # target
        self.frame.rowconfigure(5, weight=1)  # controls
        self.frame.rowconfigure(6, weight=1)  # status
        # self.frame.columnconfigure(0, weight=1)
        # self.frame.columnconfigure(1, weight=1)

        self.frame_top = self.create_row_frame(row=0, rows=1, columns=2)
        self.frame_file = self.create_row_frame(row=1, rows=1, columns=1)
        self.frame_ion = self.create_row_frame(row=2, rows=1, columns=1)
        self.frame_target_sel = self.create_row_frame(row=3, rows=1, columns=1)
        self.frame_target = self.create_row_frame(row=4, rows=1, columns=1)
        self.frame_controls = self.create_row_frame(row=5, rows=1, columns=1)
        self.frame_status = self.create_row_frame(row=6, rows=1, columns=1)

        # top

        # logo frame
        self.frame_logo = tk.Frame(self.frame_top, width=150, height=100)
        self.frame_logo.grid(row=0, column=0, sticky="NW",
                             padx=(6, 0), pady=(9, 3))
        self.frame_logo.propagate(False)

        # title text frame
        self.frame_title = tk.Frame(self.frame_top, width=350, height=100)
        self.frame_title.grid(row=0, column=1, sticky="NW",
                              padx=(6, 0), pady=(9, 3))
        self.frame_title.propagate(False)

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
                        "Start by  loading an existing file or create an input "
                        "file from scratch.")
        # Add the welcome message
        self.welcome_message_label = tk.Label(self.frame_title,
                                              font="Helvetica 9",
                                              wraplength=350,
                                              anchor=tk.W,
                                              text=welcome_text,
                                              justify=tk.LEFT)
        self.welcome_message_label.pack(expand=True, fill="both")

        # file

        # new file button
        self.frame_btn_file_new = tk.Frame(self.frame_file, width=150, height=32)
        self.frame_btn_file_new.propagate(False)
        self.frame_btn_file_new.grid(row=0, column=0, columnspan=1,
                                     sticky="NESW", padx=(6, 2), pady=2)
        self.btn_file_new = tk.Button(self.frame_btn_file_new,
                                      text="New Input File...",
                                      command=self.on_new_file)
        self.btn_file_new.pack(expand=True, fill="both")
        self.btn_file_new["state"] = "normal"

        # load file button
        self.frame_btn_file_load = tk.Frame(self.frame_file, width=200, height=32)
        self.frame_btn_file_load.propagate(False)
        self.frame_btn_file_load.grid(row=0, column=1, columnspan=1,
                                      sticky="NESW", padx=2+9, pady=2)
        self.btn_file_load = tk.Button(self.frame_btn_file_load,
                                       text="Load Existing Input File...",
                                       command=self.on_open_file)
        self.btn_file_load.pack(expand=True, fill="both")
        self.btn_file_load["state"] = "disabled"  # not implemented

        # ions

        # will be loaded in load_edit_frames()
        self.frame_label_ion = None
        self.label_ion = None
        self.frame_label_ion_name = None
        self.label_ion_name = None
        self.variable_entry_ion_name = None
        self.frame_entry_ion_name = None
        self.entry_ion_name = None
        self.frame_label_ion_energy = None
        self.label_ion_energy = None
        self.variable_entry_ion_energy = None
        self.frame_entry_ion_energy = None
        self.entry_ion_energy = None

        # target select

        self.frame_label_target = None
        self.label_target = None
        self.variable_cb_target_sel = None
        self.frame_cb_target_sel = None
        self.cb_target_sel = None

        # region frame

        self.frame_region = None
        self.btn_load_cells = None
        self.variable_cells = None

        # self.frame_region.pack(expand=True, fill="both")
        # self.frame_region.rowconfigure(0, weight=1)

        # control frame

        self.btn_open_param = None
        self.btn_save = None
        self.btn_save_as = None
        self.btn_check = None
        self.btn_run = None

        # status bar

        self.variable_entry_status = tk.StringVar()
        self.variable_entry_status.set("No file selected.")
        self.frame_entry_status = tk.Frame(self.frame_status,
                                           width=self.window_width, height=32)
        self.frame_entry_status.propagate(False)
        self.frame_entry_status.grid(row=0, column=0,
                                     sticky="NESW", padx=2, pady=2)
        self.entry_load = tk.Entry(self.frame_entry_status,
                                   textvariable=self.variable_entry_status)
        self.entry_load.pack(expand=True, fill="both")
        self.entry_load["state"] = "disabled"

        # load structure, names and content of the tables
        self.db_tables = []
        self.load_database_tables()

        # create ParameterData from database tables, this object contains
        # every parameter value and its entries
        self.parameter_data = ParameterData(self.db_tables)

        # Center the window and show it
        center_window(self)
        self.mainloop()

    def disable_editing(self):
        """ Disables the editing entries and buttons """
        self.btn_open_param["state"] = "disabled"
        self.btn_save["state"] = "disabled"
        self.btn_save_as["state"] = "disabled"
        self.btn_check["state"] = "disabled"
        self.btn_run["state"] = "disabled"

        self.entry_ion_name["state"] = "disabled"
        self.entry_ion_energy["state"] = "disabled"
        self.variable_entry_ion_name.set("")
        self.variable_entry_ion_energy.set("")

        self.cb_target_sel["state"] = "disabled"

    def enable_editing(self):
        """ Enables the editing entries and buttons """
        self.btn_open_param["state"] = "normal"
        self.btn_save["state"] = "disabled"  # not implemented
        self.btn_save_as["state"] = "disabled"  # not implemented
        self.btn_check["state"] = "disabled"  # not implemented
        self.btn_run["state"] = "disabled"  # not implemented

        self.entry_ion_name["state"] = "readonly"
        self.entry_ion_energy["state"] = "readonly"
        self.entry_ion_name.bind("<1>", self.on_entry_ion_click)
        self.entry_ion_energy.bind("<1>", self.on_entry_ion_energy_click)
        self.variable_entry_ion_name.set("<click to change>")
        self.variable_entry_ion_energy.set("<click to change>")

        self.cb_target_sel["state"] = "readonly"

    def on_new_file(self):
        """
        Opens a File Dialog to create a new file.
        """
        loaded_file = filedialog.asksaveasfile(
                initialdir=self.variable_entry_status.get(),
                title="Select IMSIL input file",
                filetypes=[("Input File", ".inp"), ("any", ".*")])
        if loaded_file:
            self.variable_entry_status.set(loaded_file.name)
            loaded_file.close()
            self.entry_load["state"] = "readonly"

            # reload default values
            self.parameter_data = ParameterData(self.db_tables)

            self.load_edit_frames()
            self.load_region_frame()
            self.enable_editing()

    def on_open_file(self):
        """
        Opens a File Dialog to open an existing file.
        """
        loaded_file = filedialog.askopenfile(
                initialdir=self.variable_entry_status.get(),
                title="Select IMSIL input file")
        if loaded_file:
            self.variable_entry_status.set(loaded_file.name)
            loaded_file.close()
            self.entry_load["state"] = "readonly"

            # TODO
            # read input file
            # load data into self.parameter_data

            self.load_edit_frames()
            self.load_region_frame()
            self.enable_editing()

    def load_edit_frames(self):
        # ions

        self.frame_label_ion = tk.Frame(self.frame_ion, width=50, height=32)
        self.frame_label_ion.grid(row=0, column=0, sticky="NW",
                                  padx=0, pady=0)
        self.frame_label_ion.propagate(False)

        self.label_ion = tk.Label(self.frame_label_ion,
                                              anchor=tk.E,
                                              text="Ions:",
                                              justify=tk.LEFT)
        self.label_ion.pack(expand=True, fill="both")

        self.frame_label_ion_name = tk.Frame(self.frame_ion, width=115, height=32)
        self.frame_label_ion_name.grid(row=0, column=1, sticky="NW",
                                       padx=0, pady=0)
        self.frame_label_ion_name.propagate(False)

        self.label_ion_name = tk.Label(self.frame_label_ion_name,
                                              anchor=tk.E,
                                              text="Chem. Name:",
                                              justify=tk.LEFT)
        self.label_ion_name.pack(expand=True, fill="both")

        self.variable_entry_ion_name = tk.StringVar()
        self.variable_entry_ion_name.set("<click to change>")
        self.frame_entry_ion_name = tk.Frame(self.frame_ion, width=120, height=24)
        self.frame_entry_ion_name.grid(row=0, column=2, sticky="NW",
                                       padx=(4, 0), pady=(4, 0))
        self.frame_entry_ion_name.propagate(False)
        self.entry_ion_name = tk.Entry(self.frame_entry_ion_name,
                                       textvariable=self.variable_entry_ion_name)
        self.entry_ion_name.pack(expand=True, fill="both")
        self.entry_ion_name["state"] = "disabled"

        self.frame_label_ion_energy = tk.Frame(self.frame_ion, width=80, height=32)
        self.frame_label_ion_energy.grid(row=0, column=3, sticky="NW",
                                         padx=0, pady=0)
        self.frame_label_ion_energy.propagate(False)

        self.label_ion_energy = tk.Label(self.frame_label_ion_energy,
                                              anchor=tk.E,
                                              text="Energy:",
                                              justify=tk.LEFT)
        self.label_ion_energy.pack(expand=True, fill="both")

        self.variable_entry_ion_energy = tk.StringVar()
        self.variable_entry_ion_energy.set("<click to change>")
        self.frame_entry_ion_energy = tk.Frame(self.frame_ion, width=120, height=24)
        self.frame_entry_ion_energy.grid(row=0, column=4, sticky="NW",
                                         padx=(4, 0), pady=(4, 0))
        self.frame_entry_ion_energy.propagate(False)
        self.entry_ion_energy = tk.Entry(self.frame_entry_ion_energy,
                                         textvariable=
                                         self.variable_entry_ion_energy)
        self.entry_ion_energy.pack(expand=True, fill="both")
        self.entry_ion_energy["state"] = "disabled"

        # target select

        self.frame_label_target = tk.Frame(self.frame_target_sel, width=50, height=32)
        self.frame_label_target.grid(row=0, column=0, sticky="NW",
                                       padx=0, pady=0)
        self.frame_label_target.propagate(False)

        self.label_target = tk.Label(self.frame_label_target,
                                              anchor=tk.E,
                                              text="Target:",
                                              justify=tk.LEFT)
        self.label_target.pack(expand=True, fill="both")

        self.variable_cb_target_sel = tk.StringVar()
        self.variable_cb_target_sel.set("Regions")
        self.frame_cb_target_sel = tk.Frame(self.frame_target_sel,
                                            width=100, height=24)
        self.frame_cb_target_sel.grid(row=0, column=1, sticky="NW",
                                       padx=(4, 0), pady=(4, 0))
        self.frame_cb_target_sel.propagate(False)
        self.cb_target_sel = ttk.Combobox(self.frame_cb_target_sel,
                                          textvariable=
                                          self.variable_cb_target_sel)
        self.cb_target_sel.pack(expand=True, fill="both")
        self.cb_target_sel["state"] = "disabled"
        self.cb_target_sel["values"] = ["Regions", "Cells"]
        self.cb_target_sel.bind('<<ComboboxSelected>>', self.cb_change)

        # control frame

        self.btn_open_param = self.create_control_btn(
                            column=0,
                            text="Parameter Editor...",
                            width=150, padx=(6, 2),
                            command=self.open_imsil_input_parameter_editor,
                            state="disabled")
        self.btn_save = self.create_control_btn(column=1, text="Save",
                                                width=80, padx=(11, 2),
                                                command=None, state="disabled")
        self.btn_save_as = self.create_control_btn(column=2, text="Save As...",
                                                   width=80, padx=(2, 2),
                                                   command=None,
                                                   state="disabled")
        self.btn_check = self.create_control_btn(column=3, text="Check",
                                                 width=80, padx=(2, 2),
                                                 command=None, state="disabled")
        self.btn_run = self.create_control_btn(column=4, text="Run",
                                               width=80, padx=(2, 2),
                                               command=None, state="disabled")

    def load_region_frame(self):
        """
        Load the Region view for the Target
        """
        if self.frame_region is not None:
            self.frame_region.destroy()
        self.frame_region = TargetFrame(self.frame_target, text="Regions",
                                        parameter_data=self.parameter_data,
                                        update_atoms=self.update_atoms)
        self.frame_region.grid(row=0, column=0, sticky="NW",
                               padx=6, pady=(0, 3))

    def load_cells_frame(self):
        """
        Load the Cells view for the Target
        """
        if self.frame_region is not None:
            self.frame_region.destroy()
        self.frame_region = tk.Frame(self.frame_target)
        self.frame_region.grid(row=0, column=0, sticky="NW",
                               padx=6, pady=(0, 3))

        frame_btn = tk.Frame(self.frame_region,
                             width=150, height=32)
        frame_btn.propagate(False)
        frame_btn.grid(row=0, column=0, columnspan=1,
                       sticky="NESW", padx=(0, 2), pady=2)
        btn = tk.Button(frame_btn, text="Load Cell File...",
                        command=self.on_open_cells_file)
        btn.pack(expand=True, fill="both")

        self.variable_cells = tk.StringVar()
        self.variable_cells.set("No file selected.")
        frame_cells_file = tk.Frame(self.frame_region,
                                           width=self.window_width - 160, height=32)
        frame_cells_file.propagate(False)
        frame_cells_file.grid(row=0, column=1,
                                     sticky="NESW", padx=2, pady=2)
        entry_load = tk.Entry(frame_cells_file,
                              textvariable=self.variable_cells)
        entry_load.pack(expand=True, fill="both")
        entry_load["state"] = "readonly"

    def on_open_cells_file(self):
        """
        Opens a File Dialog to open an existing file.
        """
        loaded_file = filedialog.askopenfile(
            initialdir=self.variable_entry_status.get(),
            title="Select Cells file")
        if loaded_file:
            self.variable_cells.set(loaded_file.name)
            loaded_file.close()
            self.entry_load["state"] = "readonly"

            self.parameter_data.set_entry_value("setup", "FILCELL", loaded_file.name)

    def cb_change(self, value):
        """
        Target Combobox change event.
        Changes Target frame to region or cell view.

        :param value: VirtualEvent passed by the event handler.
        """

        if self.variable_cb_target_sel.get() == "Regions":
            self.load_region_frame()
            self.parameter_data.set_entry_value("setup", "USECELL", "F")
        elif self.variable_cb_target_sel.get() == "Cells":
            self.load_cells_frame()
            self.parameter_data.set_entry_value("setup", "USECELL", "T")

    def on_entry_ion_click(self, event):
        """
        Callback for the on-click event of the Entry-box

        Opens a new simpledialog window that asks the user for the
        new ion name and checks for a valid molecule name.
        """
        # disable another instance of this method from opening
        self.entry_ion_name.unbind("<1>")

        # initial value for the simpledialog
        initial = "" if self.variable_entry_ion_name.get().startswith(
            "<") else self.variable_entry_ion_name.get()

        new_name = None

        # while no valid name is given
        while True:
            new_name = simpledialog.askstring(
                title="Change Ion Name",
                prompt="New Ion name:",
                initialvalue=initial,
                parent=self)
            # result of the cancel button
            if new_name is None:
                # re-enable on-click event
                self.entry_ion_name.bind("<1>", self.on_entry_ion_click)
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
                error = True

            if error:
                # info for wrong input
                tk.messagebox.showerror("Invalid Input",
                                        "Invalid Ion Name.")
            else:
                # if name is valid, proceed
                break

        # set new name if user didn't cancel
        if new_name is not None:
            self.variable_entry_ion_name.set(new_name)
            self.parameter_data.set_entry_value("ions", "NAME", new_name)
            self.update_atoms(change_ion=True)

            # re-enable on-click event
        self.entry_ion_name.bind("<1>", self.on_entry_ion_click)

    def on_entry_ion_energy_click(self, event):
        """
        Callback for the on-click event of the Entry-box

        Opens a new simpledialog window that asks the user for the
        new ion energy and checks for a valid number.
        """
        # disable another instance of this method from opening
        self.entry_ion_energy.unbind("<1>")

        # initial value for the simpledialog
        initial = "" if self.variable_entry_ion_energy.get().startswith(
            "<") else self.variable_entry_ion_energy.get()
        # new material name
        new_name = None

        # while no valid name is given
        while True:
            new_name = simpledialog.askstring(
                title="Change Ion Energy",
                prompt="New Ion Energy:",
                initialvalue=initial,
                parent=self)
            # result of the cancel button
            if new_name is None:
                # re-enable on-click event
                self.entry_ion_energy.bind("<1>", self.on_entry_ion_energy_click)
                return
            initial = new_name

            # check for correct spelling of the molecule
            try:
                float(new_name)
                # if name is valid, proceed
                if float(new_name) > 0:
                    # if name is valid, proceed
                    break
                else:
                    # info for wrong input
                    tk.messagebox.showerror("Invalid Input",
                                            "Invalid number. "
                                            "Must be real number and >0.")
            except ValueError:
                # info for wrong input
                tk.messagebox.showerror("Invalid Input",
                                        "Invalid number. "
                                        "Must be real number and >0.")

        # set new name if user didn't cancel
        if new_name is not None:
            self.variable_entry_ion_energy.set(new_name)
            self.parameter_data.set_entry_value("ions", "ENERGY", new_name)

        # re-enable on-click event
        self.entry_ion_energy.bind("<1>", self.on_entry_ion_energy_click)

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
                            if material_atoms_swap[j] == new_unique_material_atoms[i]:
                                # swap atoms
                                material_atoms_swap[i], material_atoms_swap[j] = \
                                    material_atoms_swap[j], material_atoms_swap[i]
                                self.parameter_data.swap_atom(len(ion_atoms_swap) + i,
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
        frame_btn = tk.Frame(self.frame_controls,
                             width=width, height=32)
        frame_btn.propagate(False)
        frame_btn.grid(row=0, column=column, columnspan=1,
                       sticky="NESW", padx=padx, pady=2)
        btn = tk.Button(frame_btn, text=text, command=command)
        btn.pack(expand=True, fill="both")
        btn["state"] = state
        return btn

    def create_row_frame(self, row, rows, columns):
        """
        Create a new row within this Window with
        a given number of rows and columns.
        """
        frame = tk.Frame(self.frame)
        frame.grid(row=row, column=0, sticky="NW",
                             padx=0, pady=0)
        for r in range(rows):
            frame.rowconfigure(r, weight=1)
        for c in range(columns):
            frame.rowconfigure(c, weight=1)
        return frame

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

        # self.destroy()  # Close the current Window
        self.withdraw()
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
                self.variable_cb_target_sel.set("Cells")
                filename = self.parameter_data.get_entry_value("setup",
                                                               "FILCELL")
                self.variable_cells.set(filename)
            else:
                self.load_region_frame()
                self.variable_cb_target_sel.set("Regions")

            ions = self.parameter_data.get_entry_value("ions", "NAME")
            ion_energy = self.parameter_data.get_entry_value("ions", "ENERGY")
            self.variable_entry_ion_name.set(ions)
            self.variable_entry_ion_energy.set(ion_energy)

        self.deiconify()
