import os
import tkinter as tk
from tkinter import simpledialog, ttk

from data_model.element import get_unique_atoms, get_all_elements


class TargetFrame(tk.LabelFrame):
    """
    Frame to edit the Material names. Inherits from tk.Frame.
    """
    def __init__(self, parent, text, parameter_data, update_atoms,
                 *args, **kwargs):
        """
        Init. Set up the widget layout.

        :param parent: parent frame
        :param text: Title of the frame
        :param parameter_data: contains all information
            about the imsil parameters.
        :param update_atoms: update atoms function. must be called after adding,
            removing or changing regions/atoms
        """
        super().__init__(parent, text=text, *args, **kwargs)

        self.all_elements = get_all_elements()
        self.parameter_data = parameter_data

        self.region_frames = []
        self.add_buttons = []
        self.posif_entries = []
        self.posif_values = []
        self.posif_labels = []

        # update atoms function. must be called after adding,
        # removing or changing regions/atoms
        self.update_atoms = update_atoms

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # frame to contain the region frames
        self.frame_mat_left_title = tk.Frame(self)
        self.frame_mat_left_title.grid(row=0, column=0, padx=(15, 0),
                                       pady=0, sticky="NS")

        self.label_mat = tk.Label(self.frame_mat_left_title, text="Material")
        self.label_mat.grid(row=0, column=0)

        self.frame_geom_title = tk.Frame(self)
        self.frame_geom_title.grid(row=0, column=2, padx=(15, 0),
                                       pady=0, sticky="NS")

        self.label_geom = tk.Label(self.frame_geom_title, text="Geometry")
        self.label_geom.grid(row=0, column=0)

        self.variable_cb_geom_sel = tk.StringVar()
        self.variable_cb_geom_sel.set("1D")
        self.cb_geom_sel = ttk.Combobox(self.frame_geom_title,
                                          textvariable=
                                          self.variable_cb_geom_sel,
                                          width=18)
        self.cb_geom_sel.grid(row=0, column=1, padx=3)
        self.cb_geom_sel["state"] = "readonly"
        self.cb_geom_sel["values"] = ["1D", "2D", "3D"]
        self.cb_geom_sel.bind('<<ComboboxSelected>>', self.cb_change)

        # frame to contain the region frames
        self.frame_mat_left = tk.Frame(self)
        self.frame_mat_left.grid(row=1, column=0, padx=(15, 0),
                                 pady=20, sticky="NS")

        # frame to contain the add buttons
        self.frame_mat_add = tk.Frame(self)
        self.frame_mat_add.grid(row=1, column=1,
                                pady=10, sticky="NS")

        # frame to contain the add buttons
        self.frame_geom = tk.Frame(self)
        self.frame_geom.grid(row=1, column=2,
                             pady=10, sticky="NS")

        # load every currently stored material
        self.materials = self.parameter_data.get_materials()

        # create a frame for every material.
        for i, material in enumerate(self.materials):
            self.add_region_frame(i, material, is_original=True)

        # add an empty frame when no materials are found
        if len(self.materials) == 0:
            self.add_region_frame(0, "", is_original=False)

        # setup the posif value array.
        # whenever the array gets updated,
        # the posif entries should be updated too
        posif = self.parameter_data.get_entry_value("geom", "POSIF")
        if posif.startswith("-"):
            posif = None
        elif posif[0] == "'" and posif[-1] == "'":
            posif = posif[1:-1]
            posif = posif.split(",")
            if len(posif) != len(self.region_frames) + 1:
                posif = None
        else:
            posif = None

        if posif is None:
            posif = []
            for i in range(len(self.region_frames)+1):
                posif.append("")

        self.posif_values = posif

        self.update_add_buttons()
        self.load_posif()

    def add_region_frame(self, index, material, is_original):
        """
        Add a RegionEditFrame at a given position.

        :param index: position of the frame (has to be free in the grid)
        :param material: name of the material
        :param is_original: if this function is called during initialization of
            this window
        """
        region_frame = RegionEditFrame(self.frame_mat_left,
                                       f"Region {index + 1}: ",
                                       material,
                                       self.remove_region_frame,
                                       index, self.swap_region,
                                       is_original, self.all_elements,
                                       self.parameter_data,
                                       self.update_atoms,
                                       material, index)
        region_frame.grid(row=index, column=0, sticky="WE")
        self.region_frames.insert(index, region_frame)
        self.update_add_buttons()
        self.update_region_indexes()
        self.update_all_swap_buttons()

    def remove_region_frame(self, frame):
        """
        Removes a given RegionEditFrame from the Material section.
        Also removes the region from the ParameterData and updates atoms.

        :param frame: The frame to remove
        """
        # index of the current frame in the region list
        index = self.region_frames.index(frame)

        # reconfigure all other frame grid positions after the removed one
        # to keep the numbering right
        for i in range(index, len(self.region_frames)):
            if i != 0:
                self.region_frames[i].grid(row=i - 1,
                                           column=0,
                                           sticky="WE")
                self.region_frames[i].set_label(f"Region {i}:")
                # if an original frame is removed, the indexes of the ones
                # after it need to be decreased to point to the right
                # position in the iv_dict
                if frame.is_original and self.region_frames[i].is_original:
                    self.region_frames[i].orig_index -= 1
        # actually remove the frame
        self.region_frames.remove(frame)
        frame.destroy()
        self.update_add_buttons()
        self.update_region_indexes()
        self.update_all_swap_buttons()

        # remove region from parameter_data
        self.parameter_data.remove_region(index)
        self.update_atoms(change_region=True)

        # update posif
        del self.posif_values[index + 1]
        self.update_posif_widgets()

    def swap_region(self, index1, index2):
        """
        Swaps the regions with the given indexes.
        Also effects the ParameterData and atoms.

        :param index1: Index of the first region.
        :param index2: Index of the second region.
        """
        # swap grid position
        self.region_frames[index1].grid(row=index2, column=0, sticky="WE")
        self.region_frames[index2].grid(row=index1, column=0, sticky="WE")

        # swap label text
        self.region_frames[index1].set_label("Region " + str(index2 + 1) + ":")
        self.region_frames[index2].set_label("Region " + str(index1 + 1) + ":")

        # swap list position
        self.region_frames[index1], self.region_frames[index2] = \
            self.region_frames[index2], self.region_frames[index1]

        # set correct index
        self.region_frames[index1].set_index(index2)
        self.region_frames[index2].set_index(index1)

        # update index and swap buttons
        self.update_region_indexes()
        self.update_all_swap_buttons()

        # swap parameter_data position
        self.parameter_data.swap_region(index1, index2)
        self.update_atoms(change_region=True)

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
            for i in range(len(self.add_buttons),
                           len(self.region_frames) + 1):
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

    def on_btn_add(self, sender):
        """
        Add a new Region Frame at the specified index of the button.
        Also effects the ParameterData and atoms.

        :param sender: the Button that called this method
        """
        index = self.add_buttons.index(sender)
        self.shift_region_frames(index)
        self.add_region_frame(index, "", is_original=False)

        self.update_region_indexes()
        self.update_all_swap_buttons()

        # add region to the parameter_data
        self.parameter_data.add_region_at(index)

        self.update_atoms(change_region=True)

        # update posif
        self.posif_values.insert(index + 1, "")
        self.update_posif_widgets()

    def shift_region_frames(self, index):
        """
        Shift all RegionFrames above the index to the next position in the grid.

        This is to make room for a new RegionFrame.

        :param index: Every RegionFrame above that index gets shifted.
        """
        for i, region_frame in enumerate(self.region_frames):
            if i >= index:
                region_frame.grid(row=i + 1, column=0, sticky="WE")
                region_frame.set_label(f"Region {i + 2}:")
                region_frame.set_index(i + 1)

    def update_region_indexes(self):
        """
        Updates the indexes of all region frames after a change of positions.
        """
        for i, region_frame in enumerate(self.region_frames):
            region_frame.set_index(i)

    def update_all_swap_buttons(self):
        """
        Updates the state of the swap buttons according to their position.

        Needs to be called when the amount or the position of regions is
        changed.
        """
        length = len(self.region_frames)
        for region_frame in self.region_frames:
            region_frame.update_swap_buttons(length)

    def cb_change(self, value):
        """
        Geometry Combobox change event.
        Changes Geometry frame to POSIF or geometry editor view.

        :param value: VirtualEvent passed by the event handler.
        """

        if self.variable_cb_geom_sel.get() == "1D":
            self.posif_entries.clear()
            self.load_posif()
        elif self.variable_cb_geom_sel.get() == "2D":
            self.load_geometry_editor()
        elif self.variable_cb_geom_sel.get() == "3D":
            self.load_geometry_editor()

    def load_posif(self):
        """
        Load the POSIF view for the Geometry
        """
        if self.frame_geom is not None:
            self.frame_geom.destroy()
        self.frame_geom = tk.Frame(self)
        self.frame_geom.grid(row=1, column=2,
                             pady=10, sticky="NS")

        self.update_posif_widgets()

    def load_geometry_editor(self):
        """
        Load the Geometry Editor view for the Geometry
        """
        if self.frame_geom is not None:
            self.frame_geom.destroy()
        self.frame_geom = tk.Frame(self)
        self.frame_geom.grid(row=1, column=2,
                             pady=10, sticky="NS")

        self.frame_btn_geom = tk.Frame(self.frame_geom, width=150, height=32)
        self.frame_btn_geom.propagate(False)
        self.frame_btn_geom.grid(row=0, column=0, columnspan=1,
                                     sticky="NESW", padx=(6, 2), pady=2)
        self.btn_geom = tk.Button(self.frame_btn_geom,
                                      text="Geometry Editor...",
                                      command=None)
        self.btn_geom.pack(expand=True, fill="both")
        self.btn_geom["state"] = "disabled"

    def update_posif_widgets(self):
        """
        Updates the widgets accordingly to the posif_values list.
        Also writes the posif values into parameter_data.
        """
        if self.variable_cb_geom_sel.get() == "1D":
            # too few entries -> add some
            if len(self.posif_entries) < len(self.region_frames) + 1:
                for i in range(len(self.posif_entries),
                               len(self.region_frames) + 1):
                    self.add_posif_entry()
            # too many entries -> delete excess ones
            elif len(self.posif_entries) > len(self.region_frames) + 1:
                for i in range(len(self.posif_entries) - 1,
                               len(self.region_frames), -1):
                    self.posif_entries[i].destroy()
                    self.posif_labels[-1].destroy()
                    del self.posif_entries[i]
                    del self.posif_labels[-1]

            if self.posif_values is not None:
                for i, entry in enumerate(self.posif_entries):
                    entry["state"] = "normal"
                    entry.delete(0, "end")
                    entry.insert(0, self.posif_values[i])
                    entry["state"] = "readonly"

        if self.posif_values is not None:
            # write posif into parameter_data
            posif = "\'" + ",".join(self.posif_values) + "\'"
            self.parameter_data.set_entry_value("geom", "POSIF", posif)

    def add_posif_entry(self):
        """
        Add a new "posif" entry
        """
        label_posif = tk.Label(self.frame_geom, text="POSIF:")
        label_posif.grid(row=len(self.posif_entries), column=0)
        entry_temp = tk.Entry(self.frame_geom)
        entry_temp.bind("<1>", self.on_ent_posif_click)
        entry_temp["state"] = "normal"
        entry_temp.grid(row=len(self.posif_entries), column=1, ipady=3,
                        pady=(0, 1))
        entry_temp.delete(0, "end")
        entry_temp.insert(0, "<click to change>")
        entry_temp["state"] = "readonly"
        self.posif_entries.append(entry_temp)
        self.posif_labels.append(label_posif)

    def on_ent_posif_click(self, event):
        """
        Callback for the on-click event of the Entry-box.
        Changes Region name and calls update_atoms()

        Opens a new simpledialog window that asks the user for the
        new material name and checks for a valid molecule name.
        """
        # disable another instance of this method from opening
        entry = event.widget
        entry.unbind("<1>")

        # initial value for the simpledialog
        initial = "" if entry.get().startswith("<") else entry.get()
        # new material name
        new_name = simpledialog.askstring(title="Change POSIF",
                                          prompt="New value:",
                                          initialvalue=initial,
                                          parent=self)
        # result of the cancel button
        if new_name is None:
            # re-enable on-click event
            entry.bind("<1>", self.on_ent_posif_click)
            return

        # set new name if user didn't cancel
        if new_name is not None:
            entry["state"] = "normal"
            entry.delete(0, "end")
            entry.insert(0, new_name)
            entry["state"] = "readonly"

            index = self.posif_entries.index(entry)
            self.posif_values[index] = new_name
            self.update_posif_widgets()

        # re-enable on-click event
        entry.bind("<1>", self.on_ent_posif_click)


class RegionEditFrame(tk.Frame):
    """
    Frame to edit the Material names. Inherits from tk.Frame.
    """

    def __init__(self, parent, text, material, on_delete, index, on_swap,
                 is_original, all_elements, parameter_data, update_atoms, orig_text="", orig_index=0,
                 *args, **kwargs):
        """
        Init. Set up the widget layout.

        :param parent: parent frame
        :param text: Frame Label description. Usually "Region n:"
        :param material: name of the material
        :param on_delete: callback function that gets called
            when the region is removed
        :param index: Index position of the Frame
        :param on_swap: callback function that's called when a
            swap button is pressed
        :param is_original: if this is called during initialization of the
            window
        :param all_elements: list of all elements as given by
            element.get_all_elements()
        :param parameter_data: ParameterData object containing
            the currently stored data
        :param update_atoms: callback function that needs to be called
            when ions or regions change.
        :param orig_text: original text, if the REF is original
        """
        super().__init__(parent, *args, **kwargs)

        self.on_delete = on_delete

        self.index = index
        self.on_swap = on_swap
        self.update_atoms = update_atoms

        self.all_elements = all_elements
        self.parameter_data = parameter_data

        self.is_original = is_original
        if is_original:
            self.orig_text = orig_text
            self.orig_index = orig_index

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)

        self.lbl_name = tk.Label(self, text=text)
        self.lbl_name.grid(row=0, column=0)

        self.ent_name = tk.Entry(self, width=17)
        self.ent_name.grid(row=0, column=1)
        self.ent_name.delete(0, "end")
        self.ent_name.insert(0, material)
        self.ent_name.bind("<1>", self.on_ent_click)
        if material == "":
            self.ent_name.delete(0, "end")
            self.ent_name.insert(0, "<click to change>")
        self.ent_name["state"] = "readonly"

        self.btn_up = tk.Button(self, text="up", width=20, height=20,
                                command=self.on_btn_up)
        self.set_button(self.btn_up, os.path.join("pics", "arrow_u.gif"), "up")
        self.btn_up.grid(row=0, column=3)

        self.btn_down = tk.Button(self, text="down", width=20, height=20,
                                  command=self.on_btn_down)
        self.set_button(self.btn_down, os.path.join("pics", "arrow_d.gif"),
                        "down")
        self.btn_down.grid(row=0, column=4)

        self.btn_delete = tk.Button(self, text="delete",
                                    width=20, height=20,
                                    command=self.on_btn_delete)
        self.set_button(self.btn_delete, os.path.join("pics", "minus.gif"),
                        "delete")
        self.btn_delete.grid(row=0, column=5)

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

    def on_btn_up(self):
        """
        Callback for the Up Button
        Swaps this Region with the one above it in the List and IVDict.
        """
        self.on_swap(self.index, self.index - 1)

    def on_btn_down(self):
        """
        Callback for the Down Button
        Swaps this Region with the one below it in the List and IVDict.
        """
        self.on_swap(self.index, self.index + 1)

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

    def set_name(self, name):
        """
        Sets the text in the entry box.
        """
        self.ent_name["state"] = "normal"
        self.ent_name.delete(0, "end")
        self.ent_name.insert(0, name)
        self.ent_name["state"] = "readonly"

    def set_index(self, index):
        """
        Sets the index variable for swapping.

        :param index: The index.
        """
        self.index = index

    def update_swap_buttons(self, length):
        """
        Disables the first up- and last down-swap buttons,
        so that no index error occurs.

        :param length: length of the region frames array
        """
        if self.index == 0:
            self.btn_up["state"] = "disabled"
        if self.index > 0:
            self.btn_up["state"] = "normal"
        if self.index == length - 1:
            self.btn_down["state"] = "disabled"
        if self.index < length - 1:
            self.btn_down["state"] = "normal"

    def on_ent_click(self, event):
        """
        Callback for the on-click event of the Entry-box.
        Changes Region name and calls update_atoms()

        Opens a new simpledialog window that asks the user for the
        new material name and checks for a valid molecule name.
        """
        # disable another instance of this method from opening
        self.ent_name.unbind("<1>")

        # initial value for the simpledialog
        initial = "" if self.get_name().startswith("<") else self.get_name()
        # new material name
        new_name = None

        # while no valid name is given
        while True:
            new_name = simpledialog.askstring(title="Change Material Name",
                                              prompt="New Material name:",
                                              initialvalue=initial,
                                              parent=self)
            # result of the cancel button
            if new_name is None:
                # re-enable on-click event
                self.ent_name.bind("<1>", self.on_ent_click)
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
                                        "Invalid Material Name.")
            else:
                # if name is valid, proceed
                break

        # set new name if user didn't cancel
        if new_name is not None:
            self.set_name(new_name)
            self.parameter_data.set_material_name_at(self.index, new_name)
            self.update_atoms(change_region=True)

        # re-enable on-click event
        self.ent_name.bind("<1>", self.on_ent_click)
