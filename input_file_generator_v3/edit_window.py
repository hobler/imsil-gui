"""
Functions and Class for the Edit Window

Functions:
    `center_window`
        Centers a tk window.

Classes:
    `EditWindow`
        Window for editing the Ion and Material names.
"""
import sys
import tkinter as tk
from tkinter import messagebox

from data_model.element import get_unique_atoms, get_all_elements


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
    pos_x = int(tk_window.winfo_screenwidth() / 2 - window_width / 2)
    pos_y = int(tk_window.winfo_screenheight() / 2 - window_height / 2)

    # Center the window
    tk_window.geometry("+{}+{}".format(pos_x, pos_y))
    # Show widget
    tk_window.deiconify()


class EditWindow(tk.Tk):
    """
    Edit Ion/Material Window. Inherits from tk.Tk.

    """

    def __init__(self, ions, materials, iv_dict, on_close):
        """
        Constructor.

        :param ions: Current Ion name
        :param materials: List of current Material names
        :param iv_dict: IVDict object, containing the IVArray data
        :param on_close: Callback function for returning the new data
        """
        super().__init__()

        self.on_close = on_close
        self.protocol("WM_DELETE_WINDOW", self.on_btn_cancel)
        self.ions = ions
        self.materials = materials
        self.all_elements = get_all_elements()
        self.unique_ions = get_unique_atoms([ions], self.all_elements)
        self.unique_materials = get_unique_atoms(materials, self.all_elements)
        self.iv_dict = iv_dict
        self.nr = len(materials)

        self.region_frames = []

        self.title("Edit Materials/Ions")
        self.minsize(470, 200)
        self.maxsize(500, 1000)
        self.columnconfigure(0, weight=1)
        center_window(self)

        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="WE")
        self.frame.columnconfigure(0, weight=1)

        self.frame_ion = tk.LabelFrame(self.frame, text="Ions", padx=5, pady=5)
        self.frame_ion.grid(row=0, column=0, padx=10, pady=10, sticky="WE")

        self.frame_mat = tk.LabelFrame(self.frame, text="Materials",
                                       padx=5, pady=5)
        self.frame_mat.grid(row=1, column=0, padx=10, pady=10, sticky="WE")
        self.frame_mat.rowconfigure(0, weight=1)
        self.frame_mat.columnconfigure(0, weight=1)
        self.frame_mat.columnconfigure(1, weight=1)

        self.frame_mat_left = tk.Frame(self.frame_mat)
        self.frame_mat_left.grid(row=0, column=0, padx=10,
                                 pady=10, sticky="NS")
        self.frame_mat_left.rowconfigure(0, weight=1)

        self.frame_mat_right = tk.Frame(self.frame_mat)
        self.frame_mat_right.grid(row=0, column=1,
                                  padx=10, pady=10, sticky="NS")

        self.frame_mat_control = tk.Frame(self.frame_mat_right)
        self.frame_mat_control.grid(row=0, column=0, sticky="WE")
        self.frame_mat_control.columnconfigure(0, weight=1)

        self.frame_mat_dialog = tk.Frame(self.frame_mat_right)
        self.frame_mat_dialog.grid(row=1, column=0, sticky="WE")
        self.frame_mat_dialog.columnconfigure(0, weight=1)

        self.label_ion = tk.Label(self.frame_ion, text="Ion Name:")
        self.label_ion.grid(row=0, column=0, padx=10, pady=10)
        self.entry_ion = tk.Entry(self.frame_ion)
        self.entry_ion.grid(row=0, column=1, padx=10, pady=10)
        self.entry_ion.delete(0, "end")
        self.entry_ion.insert(0, str(self.ions))

        self.btn_add_region = tk.Button(self.frame_mat_control,
                                        text="Add Region",
                                        command=self.on_btn_add_region)
        self.btn_add_region.grid(row=0, column=0,
                                 padx=10, pady=10, sticky="WE")

        self.btn_cancel = tk.Button(self.frame_mat_dialog, text="Cancel",
                                    command=self.on_btn_cancel)
        self.btn_cancel.grid(row=0, column=0, padx=10, pady=10, sticky="WE")
        self.btn_ok = tk.Button(self.frame_mat_dialog, text="OK",
                                command=self.on_btn_ok)
        self.btn_ok.grid(row=0, column=1, padx=10, pady=10, sticky="WE")

        for i, material in enumerate(self.materials):
            self.add_region_frame(i, material)

    def add_region_frame(self, index, material):
        """
        Adds a new RegionEditFrame to the Material section w
        ith a given name on a given position.

        :param index: Where to add the frame (should always be at the end)
        :param material: Name of the Material
        """
        rgn_frm = RegionEditFrame(self.frame_mat_left,
                                  "Region " + str(index + 1) + ": ",
                                  material,
                                  self.remove_region_frame)
        rgn_frm.grid(row=index, column=0, sticky="WE")
        self.region_frames.append(rgn_frm)

    def on_btn_add_region(self):
        """
        Adds a new empty RegionEditFrame at the end of the Material Section.

        """
        self.add_region_frame(len(self.region_frames), "")

    def remove_region_frame(self, frame):
        """
        Removes a given RegionEditFrame from the Material section

        :param frame: The frame to remove
        """
        index = self.region_frames.index(frame)
        # reconfigure all other frame grid positions after the removed one
        # to keep the numbering right
        if len(self.region_frames) > index:
            for i in range(index, len(self.region_frames)):
                if i != 0:
                    self.region_frames[i].grid(row=i - 1,
                                               column=0,
                                               sticky="WE")
                    self.region_frames[i].set_label("Region " + str(i) + ":")
        # actually remove the frame
        self.region_frames.remove(frame)
        frame.destroy()

    def on_btn_cancel(self):
        """
        Callback for the Cancel Button. Asks if the cancellation was intended.
        Closes the Window if the user selects "yes".

        """
        mb_result = \
            tk.messagebox.askquestion("Cancel Editing",
                                      "Are you sure you want to "
                                      "exit the Edit Window?"
                                      "\nAll unsaved changes will be lost.",
                                      icon="warning")
        if mb_result == "yes":
            self.on_close()
            self.destroy()

    def on_btn_ok(self):
        """
        Callback for the OK Button. Asks if the click was intended,
        calculates the new atoms, regions, nr and natom
        and returns them with the callback function to the main window

        """
        # get the new values from the entry boxes
        new_ion = self.entry_ion.get()
        new_materials = []
        pre_reg_len = len(self.materials)
        for rgn_frm in self.region_frames:
            new_materials.append(rgn_frm.get_name())

        # check if an entry is empty
        empty_error = False
        if new_ion == "":
            empty_error = True
        for mat in new_materials:
            if mat == "":
                empty_error = True
                break
        if empty_error:
            tk.messagebox.showerror("Invalid Input",
                                    "Ion or Materials can't be empty.")
            return

        # check for correct spelling of the molecules
        try:
            new_unique_ions = get_unique_atoms([new_ion], self.all_elements)
            new_unique_materials = get_unique_atoms(new_materials,
                                                    self.all_elements)
        except ValueError:
            tk.messagebox.showerror("Invalid Input",
                                    "Invalid Ion or Material name.")
            return

        # check if the given string was even a molecule name
        if len(new_unique_ions) == 0:
            tk.messagebox.showerror("Invalid Input", "Invalid Ion name.")
            return
        if len(new_unique_materials) == 0:
            tk.messagebox.showerror("Invalid Input", "Invalid Material name.")
            return

        # get sure that the user wants to apply the changes
        mb_result = \
            tk.messagebox.askquestion("Apply Changes",
                                      "Are you sure you want to "
                                      "apply the changes?"
                                      "\nThis may take a while.",
                                      icon="info")
        if mb_result == "no":
            return

        # calculate the regions that need to be
        # removed from the original iv_dict
        regions_to_delete = [item for item in self.materials if
                             item not in new_materials]
        # calculate the regions that need to be added to the original iv_dict
        regions_to_add = [item for item in new_materials if
                          item not in self.materials]
        # removing and adding the regions
        for region in reversed(regions_to_delete):
            self.iv_dict.remove_region(self.materials.index(region))
        for region in regions_to_add:
            self.iv_dict.add_region_at(new_materials.index(region))

        # For the Atoms do the same process
        # but for the ions and materials individually

        # calculate the atoms that need to be removed from
        # and added to the original iv_dict
        unique_ions_to_delete = \
            [item for item in self.unique_ions if
             item not in new_unique_ions]
        unique_materials_to_delete = \
            [item for item in self.unique_materials if
             item not in new_unique_materials]
        unique_ions_to_add = \
            [item for item in new_unique_ions if
             item not in set(self.unique_ions)]
        unique_materials_to_add = \
            [item for item in new_unique_materials if
             item not in self.unique_materials]

        for atom in reversed(unique_ions_to_delete):
            self.iv_dict.remove_atom(self.unique_ions.index(atom))
        for atom in unique_ions_to_add:
            self.iv_dict.add_atom_at(new_unique_ions.index(atom))

        for atom in reversed(unique_materials_to_delete):
            self.iv_dict.remove_atom(self.unique_materials.index(atom) +
                                     len(new_unique_ions))
        for atom in unique_materials_to_add:
            self.iv_dict.add_atom_at(new_unique_materials.index(atom) +
                                     len(new_unique_ions))

        # used for natom calculation
        unique_atoms = []
        unique_atoms.extend(self.unique_ions)
        unique_atoms.extend(self.unique_materials)
        # used to set the names correctly
        new_unique_atoms = []
        new_unique_atoms.extend(new_unique_ions)
        new_unique_atoms.extend(new_unique_materials)

        # calculating the new nr and natom
        natom = len(new_unique_atoms)
        nr = len(new_materials)

        # adding the new atom and region names
        # in their corresponding IVArray Entries
        for i, tab in enumerate(self.iv_dict):
            if i == 1:
                self.iv_dict[tab][3].values[0] = \
                    [x.name for x in new_unique_atoms]
            if i == 3:
                self.iv_dict[tab][1].values[0] = new_materials

        # call the callback function of the main window
        try:
            self.on_close(True, self.iv_dict, new_ion, natom, nr,
                          [x.name for x in new_unique_atoms], new_materials)
        except:
            tk.messagebox.showerror("Unexpected error:", sys.exc_info()[0])

        # destroy this window
        self.destroy()


class RegionEditFrame(tk.Frame):
    """
    Frame to edit the Material names. Inherits from tk.Frame.

    """

    def __init__(self, parent, text, material, on_delete, *args, **kwargs):
        """
        Constructor. Sets up the widget layout.

        :param parent: parent frame
        :param text: Frame Label description. Usually "Region n:"
        :param material: Name of the Material
        :param on_delete: Callback function that gets called
            when the Region is removed
        """
        super().__init__(parent, *args, **kwargs)

        self.on_delete = on_delete

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.lbl_name = tk.Label(self, text=text)
        self.lbl_name.grid(row=0, column=0)

        self.ent_name = tk.Entry(self)
        self.ent_name.grid(row=0, column=1)
        self.ent_name.delete(0, "end")
        self.ent_name.insert(0, material)

        self.btn_delete = tk.Button(self, text="delete",
                                    width=20, height=20,
                                    command=self.on_btn_delete)
        self.set_button(self.btn_delete, "minus.gif", "delete")
        self.btn_delete.grid(row=0, column=2)

    def set_button(self, widget, file, text):
        """
        Set up the Button with the specified text and picture.

        This method sets the Button image and text.

        :param widget: the Button to be set
        :param file: the name of the new image file
        :param text: the new text of the Button (for identification)
        """
        btn_new = widget
        photo_new = tk.PhotoImage(file=file, master=self)
        btn_new.config(image=photo_new)
        btn_new.image = photo_new
        btn_new.config(takefocus=False)
        btn_new.config(text=text)

    def on_btn_delete(self):
        """
        Callback for the Delete Button

        """
        self.on_delete(self)

    def set_label(self, text):
        """
        Sets the label text.

        :param text: The text.

        """
        self.lbl_name.configure(text=text)

    def get_name(self):
        """
        Returns the text in the entry box.

        """
        return self.ent_name.get()
