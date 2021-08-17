"""
Functions and Class for the Edit Window

Classes:
    `EditWindow`
        Window for editing the Ion and Material names.
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

from data_model.element import get_unique_atoms, get_all_elements
from utility import center_window


class EditWindow(tk.Tk):
    """
    Edit Ion/Material Window. Inherits from tk.Tk.

    """

    def __init__(self, ions, materials, iv_dict, on_close):
        """
        Init method.

        :param ions: Current Ion name
        :param materials: List of current Material names
        :param iv_dict: IVDict object, containing the IVArray data
        :param on_close: Callback function for returning the new data
        """
        super().__init__()

        self.on_close = on_close  # callback function
        # callback when window gets closed
        self.protocol("WM_DELETE_WINDOW", self.on_btn_cancel)
        self.ions = ions
        self.materials = materials
        self.all_elements = get_all_elements()
        self.unique_ions = get_unique_atoms([self.ions], self.all_elements)
        self.unique_materials = get_unique_atoms(self.materials, self.all_elements)
        # temporary changeable array for possible swapping
        self.ions_swap = self.unique_ions.copy()
        self.materials_swap = self.unique_materials.copy()
        self.iv_dict = iv_dict
        self.nr = len(materials)

        self.region_frames = []
        self.add_buttons = []

        # window setup
        self.title("Edit Materials/Ions")
        self.minsize(470, 200)
        self.maxsize(500, 1000)
        self.columnconfigure(0, weight=1)
        center_window(self)

        # widget setup
        # outer frame
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="WE")
        self.frame.columnconfigure(0, weight=1)

        # top left frame, containing the ion field
        self.frame_ion = tk.LabelFrame(self.frame, text="Ions", padx=5, pady=5)
        self.frame_ion.grid(row=0, column=0, padx=10, pady=5, sticky="WE")

        # bottom left frame, containing the region frame list
        self.frame_mat = tk.LabelFrame(self.frame, text="Materials",
                                       padx=5, pady=5)
        self.frame_mat.grid(row=1, column=0, padx=10, pady=5, sticky="WE")
        self.frame_mat.rowconfigure(0, weight=1)
        self.frame_mat.columnconfigure(0, weight=1)
        self.frame_mat.columnconfigure(1, weight=1)
        self.frame_mat.columnconfigure(2, weight=1)

        # frame to contain the region frames
        self.frame_mat_left = tk.Frame(self.frame_mat)
        self.frame_mat_left.grid(row=0, column=0, padx=(15, 0),
                                 pady=20, sticky="NS")

        # frame to contain the add buttons
        self.frame_mat_add = tk.Frame(self.frame_mat)
        self.frame_mat_add.grid(row=0, column=1,
                                 pady=10, sticky="NS")

        # for 'Cancel' and 'OK' button and the info label
        self.frame_right = tk.Frame(self.frame)
        self.frame_right.grid(row=0, column=1, rowspan=2, sticky="NSEW")
        self.frame_right.columnconfigure(0, weight=1)
        self.frame_right.rowconfigure(0, weight=0)
        self.frame_right.rowconfigure(1, weight=1)

        # info text frame
        self.frame_info = tk.LabelFrame(self.frame_right, text="Info")
        self.frame_info.grid(row=0, column=0, padx=10, pady=5, sticky="NSEW")
        self.frame_info.columnconfigure(0, weight=1)
        self.frame_info.rowconfigure(0, weight=1)

        # 'Cancel' and 'OK' button frame
        self.frame_dialog = tk.Frame(self.frame_right)
        self.frame_dialog.grid(row=1, column=0, padx=10, pady=5, sticky="NSEW")
        self.frame_dialog.columnconfigure(0, weight=1)
        self.frame_dialog.columnconfigure(1, weight=1)
        self.frame_dialog.rowconfigure(0, weight=1)

        # contents of ion frame
        self.label_ion = tk.Label(self.frame_ion, text="Ion Name:")
        self.label_ion.grid(row=0, column=0, padx=10, pady=10)
        self.entry_ion = tk.Entry(self.frame_ion)
        self.entry_ion.grid(row=0, column=1, padx=10, pady=10)
        self.entry_ion.delete(0, "end")
        self.entry_ion.insert(0, str(self.ions))

        self.label_info = tk.Label(self.frame_info,
                                   text="Add Ions and Materials by writing "
                                        "their molecular formula into the "
                                        "entry fields.",
                                   justify='left', wraplengt=100)
        self.label_info.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='NWE')
        self.btn_cancel = tk.Button(self.frame_dialog, text="Cancel",
                                    command=self.on_btn_cancel)
        self.btn_cancel.grid(row=1, column=0, padx=10, pady=10, sticky="WE")
        self.btn_ok = tk.Button(self.frame_dialog, text="OK",
                                command=self.on_btn_ok)
        self.btn_ok.grid(row=1, column=1, padx=10, pady=10, sticky="WE")

        for i, material in enumerate(self.materials):
            self.add_region_frame(i, material, True)

        self.update_add_buttons()

    def update_add_buttons(self):
        """
        Updates the amount of "add" buttons to the number of regions +1
        """
        if len(self.add_buttons) == len(self.region_frames) + 1:
            return
        # too many buttons -> delete excess ones
        elif len(self.add_buttons) > len(self.region_frames) + 1:
            for i in range(len(self.add_buttons) - 1,
                           len(self.region_frames), -1):
                self.add_buttons[i].destroy()
                del self.add_buttons[i]
        # too few buttons -> add some
        else:
            for i in range(len(self.add_buttons), len(self.region_frames) + 1):
                self.add_add_button()

    def add_add_button(self):
        """
        Add a new "add" button
        """
        btn_temp = tk.Button(self.frame_mat_add, text="add",
                                    width=20, height=20)
        btn_temp.config(command=lambda button=btn_temp: self.on_btn_add(button))
        self.set_button(btn_temp, os.path.join("pics", "add.gif"), "add")
        btn_temp.grid(row=len(self.add_buttons), column=0)
        self.add_buttons.append(btn_temp)

    def on_btn_add(self, sender):
        """
        Add a new Region Frame at the specified index of the button.

        :param sender: the Button that called this method
        """
        index = self.add_buttons.index(sender)
        self.shift_region_frames(index)
        self.add_region_frame(index, "", False)

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

    def add_region_frame(self, index, material, is_original):
        """
        Adds a new RegionEditFrame to the Material section w
        ith a given name on a given position.

        :param index: Where to add the frame (has to be free in the grid)
        :param material: Name of the Material
        :param is_original: If this RegionEditFrame was created while loading
            this window
        """
        rgn_frm = RegionEditFrame(self.frame_mat_left,
                                  "Region " + str(index + 1) + ": ",
                                  material,
                                  self.remove_region_frame,
                                  is_original, material, index)
        rgn_frm.grid(row=index, column=0, sticky="WE")
        self.region_frames.insert(index, rgn_frm)
        self.update_add_buttons()

    def shift_region_frames(self, index):
        """
        Shifts all RegionFrames above the index to the next position in the grid
        to make place for a new RegionFrame.

        :param index: Every RegionFrame above tha index gets shifted.
        """
        for i, rgn_frm in enumerate(self.region_frames):
            if i >= index:
                rgn_frm.grid(row=i+1, column=0, sticky="WE")
                rgn_frm.set_label("Region " + str(i+2) + ":")

    def on_btn_add_region(self):
        """
        Adds a new empty RegionEditFrame at the end of the Material Section.
        """
        self.add_region_frame(len(self.region_frames), "", False)

    def remove_region_frame(self, frame):
        """
        Removes a given RegionEditFrame from the Material section

        :param frame: The frame to remove
        """

        # index of the current frame in the region list
        index = self.region_frames.index(frame)

        # if an original material is deleted, delete it from the
        # original material list and iv_data
        if frame.is_original and frame.get_name() == frame.orig_text:
            # this line removes the entry from both
            self.iv_dict.remove_region(frame.orig_index)

        # reconfigure all other frame grid positions after the removed one
        # to keep the numbering right
        if len(self.region_frames) > index:
            for i in range(index, len(self.region_frames)):
                if i != 0:
                    self.region_frames[i].grid(row=i - 1,
                                               column=0,
                                               sticky="WE")
                    self.region_frames[i].set_label("Region " + str(i) + ":")
                    # if and original frame is removed, the indexes of the ones
                    # after it need to be decreased to point to the right
                    # position in the iv_dict
                    if frame.is_original and self.region_frames[i].is_original:
                        self.region_frames[i].orig_index -= 1
        # actually remove the frame
        self.region_frames.remove(frame)
        frame.destroy()
        self.update_add_buttons()

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
        # the indexes of newly added or changed regions
        regions_indexes = []
        # iterating reversed because some elements get deleted
        for index, rgn_frm in reversed(list(enumerate(self.region_frames))):
            new_materials.insert(0, rgn_frm.get_name())
            # if an original material was changed, delete it from the
            # original material list and iv_data
            if rgn_frm.is_original and rgn_frm.get_name() != rgn_frm.orig_text:
                # this line removes the entry from both
                self.iv_dict.remove_region(rgn_frm.orig_index)
                regions_indexes.append(index)  # append changed region
            if not rgn_frm.is_original:
                regions_indexes.append(index)  # append added region

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

        # make sure that the user wants to apply the changes
        mb_result = \
            tk.messagebox.askquestion("Apply Changes",
                                      "Are you sure you want to "
                                      "apply the changes?"
                                      "\nThis may take a while.",
                                      icon="info")
        if mb_result == "no":
            return

        # add the new regions
        for index in regions_indexes:
            self.iv_dict.add_region_at(index)

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
            index = self.unique_ions.index(atom)
            self.iv_dict.remove_atom(index)
            del self.ions_swap[index]
        for atom in unique_ions_to_add:
            self.iv_dict.add_atom_at(new_unique_ions.index(atom))
            self.ions_swap.insert(new_unique_ions.index(atom), atom.name)

        for atom in reversed(unique_materials_to_delete):
            index = self.unique_materials.index(atom)
            self.iv_dict.remove_atom(index + len(new_unique_ions))
            del self.materials_swap[index]
        for atom in unique_materials_to_add:
            self.iv_dict.add_atom_at(new_unique_materials.index(atom) +
                                     len(new_unique_ions))
            self.materials_swap.insert(new_unique_materials.index(atom),
                                       atom.name)

        # used to set the names correctly
        new_unique_atoms = []
        new_unique_atoms.extend(new_unique_ions)
        new_unique_atoms.extend(new_unique_materials)

        # check if the atoms are in order
        # and swap the contents to match the new order of atoms
        if len(new_unique_atoms) == len(self.ions_swap) + \
                                    len(self.materials_swap):

            # check and swap ions
            for i in range(len(new_unique_ions)):
                # if they aren't in order
                if new_unique_ions[i] != self.ions_swap[i]:
                    # search the right atom to swap
                    for j in range(i, len(new_unique_ions)):
                        # if the right atom index is found
                        if self.ions_swap[j] == new_unique_ions[i]:
                            # swap atoms
                            self.ions_swap[i], self.ions_swap[j] = \
                                self.ions_swap[j], self.ions_swap[i]
                            self.iv_dict.swap_atom(i, j)
                            break

            # check and swap materials
            for i in range(len(new_unique_materials)):
                # if they aren't in order
                if new_unique_materials[i] != self.materials_swap[i]:
                    # search the right atom to swap
                    for j in range(i, len(new_unique_materials)):
                        # if the right atom index is found
                        if self.materials_swap[j] == new_unique_materials[i]:
                            # swap atoms
                            self.materials_swap[i], self.materials_swap[j] = \
                                self.materials_swap[j], self.materials_swap[i]
                            self.iv_dict.swap_atom(len(self.ions_swap) + i,
                                                   len(self.ions_swap) + j)
                            break

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

    def __init__(self, parent, text, material, on_delete,
                 is_original, orig_text="", orig_index=0, *args, **kwargs):
        """
        Constructor. Sets up the widget layout.

        :param parent: parent frame
        :param text: Frame Label description. Usually "Region n:"
        :param material: Name of the Material
        :param on_delete: Callback function that gets called
            when the Region is removed
        :param is_original: If this RegionEditFrame was created while loading
            this window
        :param orig_text: original text, if the REF is original
        """
        super().__init__(parent, *args, **kwargs)

        self.on_delete = on_delete

        self.is_original = is_original
        if is_original:
            self.orig_text = orig_text
            self.orig_index = orig_index

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
        self.set_button(self.btn_delete, os.path.join("pics", "minus.gif"),
                        "delete")
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
