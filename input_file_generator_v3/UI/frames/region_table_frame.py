import os
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox

from typing import List, Callable, Tuple

from data_model.element import get_unique_atoms, Element, get_all_elements
from data_model.parameter_data import ParameterData
from utility import create_info_button_text
from UI.widgets.tooltip import create_tooltip_btn, create_custom_tooltip_btn


class RegionTableFrame(ttk.Frame):
    """
    Frame to edit the Material names. Inherits from ttk.Frame.
    """

    def __init__(self, parent,
                 update_atoms: Callable,
                 parameter_data: ParameterData,
                 geometry: str = "1D",
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parameter_data = parameter_data
        self.all_elements = get_all_elements()
        self.geometry = geometry

        self.update_atoms = update_atoms
        self.region_list = []
        self.add_buttons = []

        # surface position
        if self.geometry == '1D':
            self.surface_frame = ttk.Frame(self)
            self.surface_frame.grid(row=0, column=0, columnspan=7,
                                    sticky='we', pady=(8, 0))

            self.surface_label = ttk.Label(self.surface_frame,
                                           text="Surface position:")
            self.surface_label.grid(row=0, column=0, padx=4)

            thickness_text = (
                    "Surface Position:\n"
                    "Defines the first entry in the POSIF array. All "
                    "succeeding values are calculated by adding the "
                    "thickness value of each region to the previous "
                    "value.\n\n"
                    "POSIF:\n" +
                    create_info_button_text(
                             self.parameter_data.get_entry("geom", "POSIF")))
            self.surface_info_btn = create_custom_tooltip_btn(
                self.surface_frame, "Surface Position",
                "Surface Position (POSIF)", thickness_text)
            self.surface_info_btn.grid(row=0, column=1)

            self.surface_entry = ttk.Entry(self.surface_frame, width=17)
            self.surface_entry.grid(row=0, column=2, sticky='w', padx=4)
            self.surface_frame.columnconfigure(2, weight=1)
            self.surface_entry.delete(0, "end")
            self.surface_entry.insert(0, "")
            self.surface_entry.bind("<FocusIn>", self.on_ent_surface_focus_in)
            self.surface_entry.bind("<FocusOut>", self.on_ent_surface_focus_out)
            self.surface_entry["state"] = "normal"

            self.prev_entry_surface_pos = None

        # header of regions table
        self.material_title_frame = ttk.Frame(self)
        self.material_title_frame.grid(row=2, column=1, rowspan=2)
        self.material_label = tk.Label(self.material_title_frame,
                                       text="Material")
        self.material_label.grid(row=0, column=0, pady=(12, 0))

        self.material_info_btn = create_tooltip_btn(
            self.material_title_frame,
            self.parameter_data.get_entry("material", "NAME"))
        self.material_info_btn.grid(row=0, column=1, sticky="SW", pady=(0, 2))

        if self.geometry == '1D':
            self.thickness_title_frame = tk.Frame(self)
            self.thickness_title_frame.grid(row=2, column=2, rowspan=2) #, pady=(0, 5))
            self.thickness_label = tk.Label(self.thickness_title_frame,
                                            text="Thickness")
            self.thickness_label.grid(row=0, column=2, pady=(12, 0))
            thickness_text = (
                    "Region Thickness:\n"
                    "This parameter is directly converted into POSIF "
                    "values. POSIF starts with the \"Surface position\" "
                    "value and is incremented with each region by the "
                    "Thickness value assigned to that region.\n"
                    "Alternatively you can change POSIF directly in the "
                    "Parameter Editor under the tab \"geom\".\n\n"
                    "POSIF:\n" +
                    create_info_button_text(
                            self.parameter_data.get_entry("geom", "POSIF")))
            self.thickness_info_button = create_custom_tooltip_btn(
                    self.thickness_title_frame,
                    "Layer thickness", "Region Thickness (POSIF)",
                    thickness_text)
            self.thickness_info_button.grid(row=0, column=3,
                                            sticky="SW", pady=(0, 2))
            self.geometry_editor_btn = None
        else:
            self.geometry_editor_btn = tk.Button(self,
                                                 text="Geometry Editor...",
                                                 command=None)
            self.geometry_editor_btn.grid(row=4, column=2,
                                          rowspan=2,#len(self.region_list) * 2,
                                          sticky="NESW")
            self.geometry_editor_btn["state"] = "disabled"

        self.prev_geometry = self.geometry

        self.add_initial_regions()

    def add_initial_regions(self):
        # load every currently stored material
        self.materials = self.parameter_data.get_materials()

        thickness = []
        posif = self.parameter_data.get_entry_value("geom", "POSIF")
        if posif.startswith("-"):
            posif = None
        else:
            posif = posif.split(",")

        if posif is not None and len(posif) > 1:
            surface_pos = posif[0]
            self.set_surface_pos(surface_pos)
            for i in range(len(posif) - 1):
                try:
                    value0 = float(posif[i])
                except:
                    value0 = 0
                try:
                    value1 = float(posif[i+1])
                except:
                    value1 = 0

                if value1 <= value0:
                    thick = 0
                else:
                    thick = value1 - value0

                thickness.append(thick)

        # create a frame for every material.
        for i, material in enumerate(self.materials):
            if i < len(thickness):
                self.add_region_bar(i, material, thickness[i])
            else:
                self.add_region_bar(i, material, "")

        # add an empty frame when no materials are found
        if len(self.materials) == 0:
            self.add_region_bar(0, "", "")

    def add_region_bar(self, index, material, thickness):
        """
        Add a RegionEditFrame at a given position.

        :param index: position of the frame
        :param material: name of the material
        :param thickness: thickness of the region
        """
        region_bar = RegionTableBar(parent=self,
                                    material=material,
                                    thickness=thickness,
                                    index=index,
                                    parameter_data=self.parameter_data,
                                    all_elements=self.all_elements,
                                    update_atoms=self.update_atoms,
                                    on_delete=self.remove_region_bar,
                                    on_swap=self.swap_regions)

        self.region_list.insert(index, region_bar)
        self.set_widgets(region_bar, index)

        self.update_add_buttons()
        self.update_region_indexes()
        self.update_all_swap_buttons()
        if self.geometry == '1D':
            self.update_posif()

        if self.geometry != "1D" and self.geometry_editor_btn is not None:
            self.geometry_editor_btn.grid(row=4, column=2,
                                          rowspan=len(self.region_list) * 2,
                                          sticky="NESW")

    def set_widgets(self, region_bar, index):
        """
        Updates the grid position of the widgets contained in the region_bar

        :param region_bar: RegionTableBar contains the widgets for displaying
            region information.
        :param index: position of the bar
        """
        widgets = region_bar.get_widgets()
        for i in range(len(widgets)):
            self.rowconfigure(index*2+3, weight=1)
            self.rowconfigure(index*2+4, weight=1)
            if self.geometry != "1D" and i == 2:
                widgets[i].grid_forget()
                continue

            if i < 3:
                widgets[i].grid(row=index*2+4, column=i, rowspan=2,
                                sticky="NW", pady=(4, 0))
            else:
                widgets[i].grid(row=index*2+4, column=i, rowspan=2,
                                sticky="NW")

    def remove_widgets(self, region_bar):
        """
        Destroys the widgets contained in the region_bar.
        Removes them from the view.

        :param region_bar: RegionTableBar contains the widgets to remove.
        """
        widgets = region_bar.get_widgets()
        for i in range(len(widgets)):
            widgets[i].destroy()

    def remove_region_bar(self, bar):
        """
        Removes a given RegionTableBar from the Material section.
        Also removes the region from the ParameterData and updates atoms.

        :param bar: The bar to remove
        """
        # can't have 0 regions
        if len(self.region_list) == 1:
            return

        # index of the current frame in the region list
        index = self.region_list.index(bar)

        # actually remove the frame
        self.region_list.remove(bar)
        self.remove_widgets(bar)

        # set correct grid positions
        for i in range(index, len(self.region_list)):
            self.set_widgets(self.region_list[i], i)

        # update ui stuff
        self.update_add_buttons()
        self.update_region_indexes()
        self.update_all_swap_buttons()

        # remove region from parameter_data
        self.parameter_data.remove_region(index)
        self.update_atoms(change_region=True)

        # update posif
        self.update_posif()

    def swap_regions(self, index1, index2):
        """
        Swaps the regions with the given indexes.
        Also effects the ParameterData and atoms.

        :param index1: Index of the first region.
        :param index2: Index of the second region.
        """

        # swap list position
        self.region_list[index1], self.region_list[index2] = \
            self.region_list[index2], self.region_list[index1]

        # set correct grid positions
        self.set_widgets(self.region_list[index1], index1)
        self.set_widgets(self.region_list[index2], index2)

        # update index and swap buttons
        self.update_region_indexes()
        self.update_all_swap_buttons()

        # swap parameter_data position
        self.parameter_data.swap_region(index1, index2)
        self.update_atoms(change_region=True)

        # update posif
        self.update_posif()

    def update_add_buttons(self):
        """
        Updates the amount of "add" buttons to the number of regions +1
        """
        if len(self.add_buttons) == len(self.region_list) + 1:
            return
        # too many buttons -> delete excess ones
        elif len(self.add_buttons) > len(self.region_list) + 1:
            for i in range(len(self.add_buttons) - 1,
                           len(self.region_list), -1):
                self.add_buttons[i].destroy()
                del self.add_buttons[i]
        # too few buttons -> add some
        else:
            for i in range(len(self.add_buttons),
                           len(self.region_list) + 1):
                self.add_add_button()

    def add_add_button(self):
        """
        Add a new "add" button
        """
        btn_temp = tk.Button(self, text="add",
                             width=20, height=20)
        btn_temp.config(command=lambda button=btn_temp: self.on_btn_add(button))
        self.set_button(btn_temp, os.path.join("pics", "add.gif"), "add")
        if len(self.add_buttons) == 0:
            btn_temp.grid(row=3,
                          column=6, rowspan=2, pady=(23, 0))
        else:
            btn_temp.grid(row=len(self.add_buttons)*2+3, column=6, rowspan=2)
        # force the button to steal focus when clicked
        btn_temp.bind("<1>", lambda event: btn_temp.focus_set())
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

    def shift_region_frames(self, index):
        """
        Shift all RegionFrames above the index to the next position in the grid.
        This is used to make room for a new RegionFrame.

        :param index: Every RegionFrame above that index gets shifted.
        """
        for i, region_bar in enumerate(self.region_list):
            if i >= index:
                self.set_widgets(region_bar, i+1)
                region_bar.update_index()

    def on_btn_add(self, sender):
        """
        Add a new Region Frame at the specified index of the button.
        Also effects the ParameterData and atoms.

        :param sender: the Button that called this method
        """
        index = self.add_buttons.index(sender)

        self.shift_region_frames(index)
        self.add_region_bar(index, "", "")

        self.update_region_indexes()
        self.update_all_swap_buttons()

        # add region to the parameter_data
        self.parameter_data.add_region_at(index)

        self.update_atoms(change_region=True)

    def update_region_indexes(self):
        """
        Updates the indexes of all region frames after a change of positions.
        """
        for i, region_bar in enumerate(self.region_list):
            region_bar.update_index()

    def update_all_swap_buttons(self):
        """
        Updates the state of the swap buttons according to their position.

        Needs to be called when the amount or the position of regions is
        changed.
        """
        length = len(self.region_list)
        for region_bar in self.region_list:
            region_bar.update_swap_buttons(length)

    #def switch_geometry(self, geometry):
    #    """
    #    Switches between the different modes [1D, 2D, 3D].
    #    Shows thickness at 1D and Geometry editor at 2D and 3D.

     #   :param geometry: string that represents the mode [1D, 2D, 3D].
     #   """

     #   if geometry == self.prev_geometry:
     #       return

     #   self.geometry = geometry
     #   for i, region_bar in enumerate(self.region_list):
     #       self.set_widgets(region_bar, i)
     #   if geometry == "1D":
     #       self.thickness_title_frame.grid(row=2, column=2, rowspan=2, pady=(0, 5))
     #       self.frame_surface_lbl.grid(row=0, column=1, rowspan=2, pady=(10, 0))
     #       self.frame_surface_entry.grid(row=0, column=2, rowspan=2, pady=(10, 0))
     #       #self.surface_frame.grid(row=0, column=1, rowspan=2, pady=(10, 0))
     #       self.geometry_editor_btn.destroy()
     #       self.geometry_editor_btn = None
     #   elif geometry == "2D" or geometry == "3D":
     #       self.thickness_title_frame.grid_forget()
     #       self.frame_surface_lbl.grid_forget()
     #       self.frame_surface_entry.grid_forget()
     #       #self.surface_frame.grid_forget()
     #       if self.geometry_editor_btn is None:
     #           self.geometry_editor_btn = tk.Button(self,
     #                                                text="Geometry Editor...",
     #                                                command=None)
     #           self.geometry_editor_btn.grid(row=4, column=2,
     #                                         rowspan=len(self.region_list)*2,
     #                                         sticky="NESW")
     #           self.geometry_editor_btn["state"] = "disabled"
     #   else:
     #       pass

     #   self.prev_geometry = geometry

    def get_posif(self):
        """
        calculates the POSIF values from the thickness and
        returns the POSIF string.

        :return: POSIF string
        """
        surface_pos = self.get_surface_pos()
        try:
            surface_pos = float(surface_pos)
        except:
            surface_pos = 0

        posif_values = [str(surface_pos)]

        for region_bar in self.region_list:
            thickness = region_bar.get_thickness()
            if thickness == "":
                thickness = 0
            else:
                thickness = float(thickness)
            surface_pos += thickness
            posif_values.append(str(surface_pos))

        return ",".join(posif_values)

    def update_posif(self):
        """
        writes the POSIF string to the parameter_data.
        """
        posif = self.get_posif()
        self.parameter_data.set_entry_value("geom", "POSIF", posif)

    def get_surface_pos(self):
        """
        Returns the surface position.
        """
        return self.surface_entry.get()

    def set_surface_pos(self, surface_pos):
        """
        Sets the text in the thickness box.
        """
        if self.geometry == '1D':
            self.surface_entry.delete(0, "end")
            self.surface_entry.insert(0, surface_pos)

    def on_ent_surface_focus_in(self, event):
        """
        Callback for getting focus on the thickness entry box
        """
        self.prev_entry_surface_pos = self.get_surface_pos()

    def on_ent_surface_focus_out(self, event):
        """
        Callback for the on-click event of the thickness Entry-box.

        Updates POSIF values accordingly if value is a number.
        """
        # disable another instance of this method from opening
        self.surface_entry.unbind("<FocusOut>")

        # initial value for the simpledialog
        initial = self.get_surface_pos()
        # new material thickness
        new_surface_pos = initial
        first = True

        # while no valid number is given
        while True:
            if not first:
                new_surface_pos = simpledialog.askstring(title="Change surface position",
                                                         prompt="New surface position:",
                                                         initialvalue=initial,
                                                         parent=self)
            first = False
            # result of the cancel button
            if new_surface_pos is None:
                # re-enable on-click event
                self.set_surface_pos(self.prev_entry_surface_pos)
                self.surface_entry.bind("<FocusOut>", self.on_ent_surface_focus_out)
                return
            initial = new_surface_pos

            # check for correct spelling of the molecule
            number = None
            try:
                number = float(new_surface_pos)
            except ValueError:
                error = True
            else:
                error = False

            if new_surface_pos == "":
                error = False

            if error:
                # info for wrong input
                tk.messagebox.showerror("Invalid Input",
                                        "Invalid surface position. "
                                        "Enter a valid number.")
            else:
                # if thickness is valid, proceed
                break

        # set new thickness if user didn't cancel
        if new_surface_pos is not None:
            self.set_surface_pos(new_surface_pos)
            self.update_posif()

        # re-enable on-click event
        self.surface_entry.bind("<FocusOut>", self.on_ent_surface_focus_out)


class RegionTableBar:
    """
    Structure that holds the widgets and helper functions for displaying the
    Region in the RegionTableFrame.
    """

    def __init__(self, parent: RegionTableFrame,
                 material: str,
                 thickness: str,
                 index: int,
                 parameter_data: ParameterData,
                 all_elements: List[Element],
                 update_atoms: Callable,
                 on_delete: Callable,
                 on_swap: Callable):

        self.parent = parent
        self.parameter_data = parameter_data

        self.update_atoms = update_atoms
        self.on_delete = on_delete
        self.on_swap = on_swap

        self.all_elements = all_elements

        self.prev_entry_val = ""
        self.prev_entry_thick_val = ""

        # create widgets
        self.lbl_region = ttk.Label(parent, text="Region "+str(index+1))
        self.lbl_region.grid(row=0, column=0, padx=4)

        self.ent_name = tk.Entry(parent, width=17)
        self.ent_name.grid(row=0, column=1)
        self.ent_name.delete(0, "end")
        self.ent_name.insert(0, material)
        self.ent_name.bind("<FocusIn>", self.on_ent_name_focus_in)
        self.ent_name.bind("<FocusOut>", self.on_ent_name_focus_out)
        self.ent_name["state"] = "normal"

        self.ent_thick = tk.Entry(parent, width=17)
        self.ent_thick.grid(row=0, column=2)
        self.ent_thick.delete(0, "end")
        self.ent_thick.insert(0, thickness)
        self.ent_thick.bind("<FocusIn>", self.on_ent_thick_focus_in)
        self.ent_thick.bind("<FocusOut>", self.on_ent_thick_focus_out)
        self.ent_thick["state"] = "normal"

        self.btn_up = tk.Button(parent, text="up", width=20, height=20,
                                command=self.on_btn_up)
        self.set_button(self.btn_up, os.path.join("pics", "arrow_u.gif"), "up")
        self.btn_up.grid(row=0, column=3)

        self.btn_down = tk.Button(parent, text="down", width=20, height=20,
                                  command=self.on_btn_down)
        self.set_button(self.btn_down, os.path.join("pics", "arrow_d.gif"),
                        "down")
        self.btn_down.grid(row=0, column=4)

        self.btn_delete = tk.Button(parent, text="delete",
                                    width=20, height=20,
                                    command=self.on_btn_delete)
        self.set_button(self.btn_delete, os.path.join("pics", "minus.gif"),
                        "delete")
        self.btn_delete.grid(row=0, column=5)

        # force the button to steal focus when clicked
        # so that the focusout event gets called on the entries
        self.btn_delete.bind("<1>", lambda event: self.btn_delete.focus_set())
        self.btn_up.bind("<1>", lambda event: self.btn_up.focus_set())
        self.btn_down.bind("<1>", lambda event: self.btn_down.focus_set())

    def set_button(self, widget, file, text):
        """
        Set up the Button with the specified text and picture.

        This method sets the Button image and text.

        :param widget: the Button to be set
        :param file: the name of the new image file
        :param text: the new text of the Button (for identification)
        """
        btn_new = widget
        photo_new = tk.PhotoImage(file=file, master=self.parent)
        btn_new.config(image=photo_new)
        btn_new.image = photo_new
        btn_new.config(takefocus=False)
        btn_new.config(text=text)

    def get_widgets(self) -> Tuple[tk.Label, tk.Entry, tk.Entry,
                                   tk.Button, tk.Button, tk.Button]:
        """
        Returns the widgets.

        :return: Label, Entry Name, Entry Thickness, Button Up, Button Down, Button Delete.
        """
        return (self.lbl_region, self.ent_name, self.ent_thick,
                self.btn_up, self.btn_down, self.btn_delete)

    def get_index(self):
        """
        Returns the index of the region.
        """
        return self.parent.region_list.index(self)

    def get_name(self):
        """
        Returns the text in the name box.
        """
        return self.ent_name.get()

    def set_name(self, name):
        """
        Sets the text in the name box.
        """
        self.ent_name.delete(0, "end")
        self.ent_name.insert(0, name)

    def get_thickness(self):
        """
        Returns the text in the thickness box.
        """
        return self.ent_thick.get()

    def set_thickness(self, thickness):
        """
        Sets the text in the thickness box.
        """
        self.ent_thick.delete(0, "end")
        self.ent_thick.insert(0, thickness)

    def update_index(self):
        """
        Updates the Label text to the correct index.
        """
        index = self.get_index()
        self.lbl_region["text"] = "Region " + str(index+1) + ":"

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
        index = self.get_index()
        self.on_swap(index, index - 1)

    def on_btn_down(self):
        """
        Callback for the Down Button
        Swaps this Region with the one below it in the List and IVDict.
        """
        index = self.get_index()
        self.on_swap(index, index + 1)

    def update_swap_buttons(self, length):
        """
        Disables the first up- and last down-swap buttons,
        so that no index error occurs.

        :param length: length of the region frames array
        """
        index = self.get_index()
        if index == 0:
            self.btn_up["state"] = "disabled"
        if index > 0:
            self.btn_up["state"] = "normal"
        if index == length - 1:
            self.btn_down["state"] = "disabled"
        if index < length - 1:
            self.btn_down["state"] = "normal"

    def on_ent_name_focus_in(self, event):
        """
        Callback for getting focus on the name entry box
        """
        self.prev_entry_val = self.get_name()

    def on_ent_name_focus_out(self, event):
        """
        Callback for the on-click event of the Entry-box.
        Changes Region name and calls update_atoms()

        Opens a new simpledialog window that asks the user for the
        new material name and checks for a valid molecule name.
        """
        # disable another instance of this method from opening
        self.ent_name.unbind("<FocusOut>")

        # initial value for the simpledialog
        initial = self.get_name()
        # new material name
        new_name = initial
        first = True

        # while no valid name is given
        while True:
            if not first:
                new_name = simpledialog.askstring(title="Change Material Name",
                                                  prompt="New Material name:",
                                                  initialvalue=initial,
                                                  parent=self.parent)
            first = False
            # result of the cancel button
            if new_name is None:
                # re-enable on-click event
                self.set_name(self.prev_entry_val)
                self.ent_name.bind("<FocusOut>", self.on_ent_name_focus_out)
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
                                        "Invalid Material Name.")
            else:
                # if name is valid, proceed
                break

        # set new name if user didn't cancel
        if new_name is not None:
            self.set_name(new_name)
            self.parameter_data.set_material_name_at(self.get_index(), new_name)
            self.update_atoms(change_region=True)

        # re-enable on-click event
        self.ent_name.bind("<FocusOut>", self.on_ent_name_focus_out)

    def on_ent_thick_focus_in(self, event):
        """
        Callback for getting focus on the thickness entry box
        """
        self.prev_entry_thick_val = self.get_thickness()

    def on_ent_thick_focus_out(self, event):
        """
        Callback for the on-click event of the thickness Entry-box.

        Updates POSIF values accordingly if value is a number.
        """
        # disable another instance of this method from opening
        self.ent_thick.unbind("<FocusOut>")

        # initial value for the simpledialog
        initial = self.get_thickness()
        # new material thickness
        new_thickness = initial
        first = True

        # while no valid number is given
        while True:
            if not first:
                new_thickness = simpledialog.askstring(title="Change Material thickness",
                                                       prompt="New Material thickness:",
                                                       initialvalue=initial,
                                                       parent=self.parent)
            first = False
            # result of the cancel button
            if new_thickness is None:
                # re-enable on-click event
                self.set_thickness(self.prev_entry_thick_val)
                self.ent_thick.bind("<FocusOut>", self.on_ent_thick_focus_out)
                return
            initial = new_thickness

            # check for correct spelling of the molecule
            number = None
            try:
                number = float(new_thickness)
            except ValueError:
                error = True
            else:
                error = False

            if new_thickness == "":
                error = False

            if error:
                # info for wrong input
                tk.messagebox.showerror("Invalid Input",
                                        "Invalid Material Thickness. "
                                        "Enter a valid number.")
            else:
                # if thickness is valid, proceed
                break

        # set new thickness if user didn't cancel
        if new_thickness is not None:
            self.set_thickness(new_thickness)
            self.parent.update_posif()

        # re-enable on-click event
        self.ent_thick.bind("<FocusOut>", self.on_ent_thick_focus_out)

