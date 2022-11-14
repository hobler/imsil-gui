import tkinter as tk
from tkinter import ttk

from UI.frames.region_table_frame import RegionTableFrame


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

        self.parameter_data = parameter_data

        self.region_list = []
        self.add_buttons = []

        # update atoms function. must be called after adding,
        # removing or changing regions/atoms
        self.update_atoms = update_atoms

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.frame_geom_title = tk.Frame(self)
        self.frame_geom_title.grid(row=0, column=0, padx=(15, 0),
                                       pady=0, sticky="NSW")

        self.label_geom = tk.Label(self.frame_geom_title, text="Geometry")
        self.label_geom.grid(row=0, column=0)

        self.variable_cb_geom_sel = tk.StringVar()
        self.variable_cb_geom_sel.set("1D")
        self.cb_geom_sel = ttk.Combobox(self.frame_geom_title,
                                          textvariable=
                                          self.variable_cb_geom_sel,
                                          width=3)
        self.cb_geom_sel.grid(row=0, column=1, padx=3)
        self.cb_geom_sel["state"] = "readonly"
        self.cb_geom_sel["values"] = ["1D", "2D", "3D"]
        self.cb_geom_sel.bind('<<ComboboxSelected>>', self.cb_change)
        # force the Combobox to steal focus when scrolled
        self.cb_geom_sel.bind("<MouseWheel>",
                                lambda event: self.cb_geom_sel.focus_set())

        self.region_table = RegionTableFrame(self, self.update_atoms,
                                             self.parameter_data)
        self.region_table.grid(row=2, column=0, padx=(30, 90),
                               pady=(0, 10), sticky="NS")

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
            self.region_table.set_surface_pos(surface_pos)
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
                self.region_table.add_region_bar(i, material, thickness[i])
            else:
                self.region_table.add_region_bar(i, material, "")

        # add an empty frame when no materials are found
        if len(self.materials) == 0:
            self.region_table.add_region_bar(0, "", "")

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

    def cb_change(self, value):
        """
        Geometry Combobox change event.
        Changes Geometry frame to POSIF or geometry editor view.

        :param value: VirtualEvent passed by the event handler.
        """
        self.region_table.switch_geometry(self.variable_cb_geom_sel.get())
