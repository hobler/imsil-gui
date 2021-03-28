"""
Classes:
    :WelcomeWindow: The main window, where the user can configure the
                    Input Parameter Editor settings.
    :ImsilInputParameterEditor: Based on the four parameters (type of
                    simulation, existing input file, number of regions
                    and number of atoms) the IMSIL Input Parameter
                    Editor will be opened.
"""
import os
import sys
import tkinter as tk

from collections import OrderedDict
from tkinter import ttk, filedialog

from data_model.input_file import InputFile
from data_model.read_sqlite import get_database_table_names
from UI.Frames.blanc_frame import BlancFrame
from UI.Frames.tab_frame import TabFrame
from UI.Frames.blanc_frame import WELCOME
from edit_window import EditWindow
from data_model.iv_data import IVData, IVDict

DATABASE_FILE = "parameters.db"


def read_existing_input_file(file_path):
    """
    Read an existing input file

    Use the path file_path to read the file with the f90nml package in
    the InputFile class. It can be used for further work reading an
    input file and filling the GUI with the parameter values from the
    file.

    :param file_path: path of an IMSIL input file
    :return: InputFile instance if file exist, otherwise None
    """
    if os.path.isfile(file_path):
        input_file = InputFile(file_path)
        return input_file
    else:
        print(file_path + " doesn't exist.")
        return None


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
                        " for IMSIL. Start with either loading edit an "
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
        # Open the ImsilInputParameterEditor
        ImsilInputParameterEditor(
            type_of_simulation=self.type_sim_combobox_variable.get(),
            input_file_path=self.load_existing_file_variable.get(),
            nr=self.nr_var,
            natom=self.natom_var)


class ImsilInputParameterEditor:
    """
    This is the class for the Imsil Input Parameter Editor.

    The IMSIL Input Parameter Editor consists of a notebook with tabs,
    where each tab corresponds to a database table.
    """

    def __init__(self, type_of_simulation, input_file_path, nr, natom):
        """
        In the initialization of the IMSIL Input Parameter Editor a
        notebook is added to the window. For each table of the database
        a new tab is added as a TabFrame to the notebook.

        If a path to an input file is passed, it is read and the
        parameter values will be placed into the Editor.

        :param type_of_simulation: type of the simulation
        :param input_file_path: path of an existing input file
        :param nr: (textvariable) number of regions for index variable arrays
        :param natom: (textvariable) number of atoms for index variable arrays
        """
        if not os.path.isfile(DATABASE_FILE):
            sys.exit(DATABASE_FILE + " does not exist.")

        # Create the root window, adjust its title, make it non-
        # resizable and center it
        self.root = tk.Tk()
        self.root.title('IMSIL Input Parameter Editor')
        self.root.resizable(False, False)
        center_window(self.root)

        # Add a loading message (becomes visible after the user presses
        # the button to open the IMSIL Input Parameter Editor in the
        # Welcome Window)
        label = tk.Label(self.root, text="Loading data...")
        label.pack()

        # Create the Notebook
        self.nb = ttk.Notebook(self.root, width=900, height=600)

        # Add the necessary tabs
        for table_name in get_database_table_names(DATABASE_FILE):
            tab_frame = TabFrame(parent=self.nb,
                                 db_file=DATABASE_FILE,
                                 table_name=table_name,
                                 type_of_simulation=type_of_simulation,
                                 nr=nr,
                                 natom=natom,
                                 name=table_name)
            self.nb.add(tab_frame, text=table_name)

        # Remove the loading message
        label.pack_forget()
        # Place the notebook
        self.nb.grid(row=0, column=0, sticky="NESW")

        self.nr = nr
        self.natom = natom

        # creating a menu bar
        # can also be used to read in files or save files later
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        filemenu = tk.Menu(self.menu)
        editmenu = tk.Menu(self.menu)
        viewmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=filemenu)
        self.menu.add_cascade(label="Edit", menu=editmenu)
        editmenu.add_command(label="Materials/Ions",
                             command=self.open_edit_material_window)
        self.menu.add_cascade(label="View", menu=viewmenu)

        # If the user has passed the name of an IMSIL input file
        if input_file_path != "":
            # Read IMSIL input file
            input_file = read_existing_input_file(input_file_path)
            if input_file is not None:
                # Go through all params that are defined in the file
                for record in input_file.nml.keys():
                    for par_name in input_file.nml[record]:
                        if not isinstance(par_name, OrderedDict):
                            # Set parameter value in tab
                            self.set_parameter_value(
                                tab_name=record,
                                parameter_name=par_name,
                                parameter_value=input_file.nml[record][
                                    par_name])

        # Center the window again, since it changed size and show it
        center_window(self.root)
        self.root.mainloop()

    #    def get_all_parameter_values(self):
    #        """
    #        Go through all tabs in the notebook and use the ui_data_list
    #        with the stored (default) values of the parameters to get all
    #        changes.
    #
    #        This function can be used later to generate the input file.
    #
    #        Currently this function is not in use!
    #        """
    #        for nb_tab in self.nb.tabs():
    #            frame = self.nb.nametowidget(nb_tab)
    #            if hasattr(frame.scroll_frame, 'ui_data_list'):
    #                # frame_ui_data_list = frame.scroll_frame.ui_data_list
    #                pass

    def set_parameter_value(self, tab_name, parameter_name, parameter_value):
        """
        Set value of a parameter in the specified tab of the notebook.

        :param tab_name: name of the notebook tab as string
        :param parameter_name: name of the parameter as string
        :param parameter_value: parameter value to be set as a string

        EXAMPLE:
            set_parameter_value("setup", "ndim", "2")
        """
        tab_frame = self.nb.nametowidget(tab_name)
        if tab_frame is not None:
            if hasattr(tab_frame.scroll_frame, 'ui_data_list'):
                par_variable = tab_frame.scroll_frame.ui_data_list.get_variable(
                    parameter_name)
                if par_variable is not None:
                    par_variable.set(parameter_value)
                else:
                    print("There is no parameter with the name "
                          + parameter_name + " in tab " + tab_name)
            else:
                print("Frame "
                      + tab_frame
                      + " does not contain an attribute with the name"
                      + " ui_data_list")
        else:
            print("There is no tab with the name " + tab_name)

    def update_all_iv_arrays(self, iv_dict, natom, nr):
        """
        Resizes all IndexVariableArrays in every Tab.

        :param iv_dict: dictionary containing all ivarrays
            accessible through the tab_name
        :param nr: new number of Regions
        :param natom: new number of Atoms
        """

        # can't set the variables below 1
        if nr < 1 or natom < 1:
            return

        # save the current tab to reopen later
        current_tab = self.nb.select()
        # disable all tabs so no entries can be made while updating
        self.disable_tabs()

        # Add ProgressBars and Labels to show the progress of the resizing
        progressbar_tab = ttk.Progressbar(self.root)
        progressbar_tab.grid(row=1, column=0, sticky="NESW")
        progress_tab_label = ttk.Label(self.root)
        progress_tab_label.grid(row=2, column=0, sticky="NESW")
        progressbar_array = ttk.Progressbar(self.root)
        progressbar_array.grid(row=3, column=0, sticky="NESW")
        progress_array_label = ttk.Label(self.root)
        progress_array_label.grid(row=4, column=0, sticky="NESW")
        # update the window to show the new elements
        self.root.update()

        # save previous size
        if type(self.nr) == int:
            nr_pre = self.nr
        else:
            nr_pre = self.nr.get()
        if type(self.natom) == int:
            natom_pre = self.natom
        else:
            natom_pre = self.natom.get()

        # loop over all tabs
        for tab_num, tab_name in enumerate(self.nb.tabs()):

            # Set the progress Label to the current tab name
            progress_tab_label['text'] = "Updating Tab: " \
                                         + tab_name.split('.')[-1]
            progress_array_label['text'] = "Clearing all IVArrays"
            progressbar_array["value"] = 0
            self.root.update()

            # ---- Clear all IVArrays ----
            # Get TabFrame to access the scroll_frame
            tab_frame = self.nb.nametowidget(tab_name)
            # Clear the IVArray dependencies in the ui_data_list
            # TODO better way?
            for i in reversed(
                    range(
                        len(tab_frame.scroll_frame.ui_data_list.data_list))):
                if "indexvariable" in \
                        str(tab_frame.scroll_frame.ui_data_list.data_list[i]):
                    tab_frame.scroll_frame.ui_data_list.data_list.remove(
                        tab_frame.scroll_frame.ui_data_list.data_list[i])
            # Clear the pre-saved list of IVArrays (scroll_frame.ivarray_list)
            self.clear_ivarray_list_in_tab(tab_name)
            # Delete the IVArrays
            self.delete_all_ivarrays_in_tab(tab_name)

            # ---- add new arrays with new size ----
            for arr_num, ivdata in enumerate(iv_dict[tab_name]):
                # update progress label
                progress_array_label['text'] = "Re-adding IVArray " \
                                               + str(arr_num) \
                                               + "/" \
                                               + str(len(iv_dict[tab_name]))
                self.root.update()

                # adding ivarray
                self.add_ivarray_to_tab(tab_name, nr, natom, ivdata.array_settings)

                # update progressbar
                progressbar_array["value"] = \
                    100 * (arr_num + 1) / len(iv_dict[tab_name])
                self.root.update()

            # ---- re-add values, cut off excess ones and add zeros ----
            tab_ivarrays = self.get_ivarrays_from_tab(tab_name)
            assert len(tab_ivarrays) == len(iv_dict[tab_name])
            for i, ivarray in enumerate(tab_ivarrays):
                # update progress label
                progress_array_label['text'] = "Re-adding Values to IVArray " \
                                               + str(i) \
                                               + "/" \
                                               + str(len(tab_ivarrays))
                self.root.update()

                # re-adding values
                ivarray.set_values_from_ivdata(iv_dict[tab_name][i], nr, natom)

                # update progressbar
                progressbar_array["value"] = \
                    100 * (i + 1) / len(tab_ivarrays)
                self.root.update()

            # update progressbar value
            progressbar_tab["value"] = \
                100 * (tab_num + 1) / len(self.nb.tabs())
            self.root.update()

        # save new size
        self.nr = nr
        self.natom = natom

        # remove progressbar and label
        progressbar_tab.destroy()
        progress_tab_label.destroy()
        progressbar_array.destroy()
        progress_array_label.destroy()

        # Enable all tabs again after finishing
        self.enable_tabs()
        # Reopen the before opened Tab
        self.nb.select(current_tab)

    def get_ivarrays_from_tab(self, tab_name):
        """
        Returns the IndexVariableArrays of the Tab with the specified name.

        :param tab_name: Name of the Tab that should return the Arrays.
        :return: List of IndexVariableArrays that are contained in the Tab.
        If the Tab doesn't exist return None.
        """
        tab_frame = self.nb.nametowidget(tab_name)
        if tab_frame is not None:
            return tab_frame.get_ivarrays()
        else:
            return None

    def clear_ivarray_list_in_tab(self, tab_name):
        """
        Calls the clear_ivarray_list function for every Tab.

        :param tab_name: Name of the Tab that should return the Arrays.
        """
        tab_frame = self.nb.nametowidget(tab_name)
        if tab_frame is not None:
            tab_frame.clear_ivarray_list()

    def delete_all_ivarrays_in_tab(self, tab_name):
        """
        Deletes every ivarray in the given Tab

        :param tab_name: Name of the Tab, where the arrays get deleted.
        """
        tab_frame = self.nb.nametowidget(tab_name)
        scroll_frame = tab_frame.scroll_frame
        content_frame_entry = scroll_frame.content_frame

        for child in content_frame_entry.winfo_children():
            if "indexvariable" in str(child):
                child.destroy()

    def add_ivarray_to_tab(self, tab_name, nr, natom, array_settings):
        """
        Adds a new ivarray to the given Tab with the new size
        and sets the structure based on the values[2] array state.
        e.g. par_name, index_var_list, ... see below code

        :param tab_name: Name of the Tab, where the array gets added.
        :param nr: Number of regions.
        :param natom: Number of atoms.
        :param array_settings: Values from the previous array defined by get_values().
        """
        tab_frame = self.nb.nametowidget(tab_name)
        if tab_frame is not None:
            self.change_dim_of_scroll_frame(tab_frame.scroll_frame, nr, natom)
            tab_frame.scroll_frame.add_parameter(
                array_settings[0],  # par_name
                array_settings[1],  # index_var_list
                array_settings[2],  # default_value
                array_settings[3],  # short_desc
                array_settings[4],  # long_desc
                False,  # is_bool
                True)  # row_index

    def change_dim_of_scroll_frame(self, scroll_frame, nr, natom):
        """
        Change the size variables in the scroll_frame

        :param scroll_frame: scroll_frame of the Tab.
        :param nr: Number of regions.
        :param natom: Number of atoms.
        """
        scroll_frame.nr = nr
        scroll_frame.natom = natom

    def disable_tabs(self):
        """
        Disables all Tabs of the notebook.

        """
        for i in range(len(self.nb.tabs())):
            self.nb.tab(i, state="disabled")

    def enable_tabs(self):
        """
        Enables all Tabs of the notebook.

        """
        for i in range(len(self.nb.tabs())):
            self.nb.tab(i, state="normal")

    def open_edit_material_window(self):
        """
        Opens the window for editing the Ion and Material names.

        """

        # get all data
        iv_dict = self.get_data_from_ivarrays()
        ions = None
        materials = []

        #   get current Ion + Materials
        for tab_num, tab_name in enumerate(self.nb.tabs()):
            # ion is saved on the 3rd tab (ions) in the entry box entry8
            if tab_num == 2:
                # get all the parent frames to get to the entries
                tab_frame = self.nb.nametowidget(tab_name)
                scroll_frame = tab_frame.scroll_frame
                content_frame_entry = scroll_frame.content_frame_entry

                for child in content_frame_entry.winfo_children():
                    if "entry8" in str(child):
                        ions = child.get()
            # materials are saved in an IndexVariableArray on tab 4 (material)
            elif tab_num == 3:
                # can be read from the iv_dict because it's already read before
                # 2nd iv_array -> 1, 1st entry -> 0
                materials = iv_dict[tab_name][1].values[0]
                break

        # hide this window
        self.root.withdraw()
        # open edit window with callback function to return new ivdata
        edit_window = EditWindow(ions, materials, iv_dict,
                                 self.on_close_edit_material_window)

    def on_close_edit_material_window(self, change=False, iv_dict=None,
                                      new_ion=None, natom=0, nr=0,
                                      atoms=None, regions=None):
        """
        Callback function. Gets called when the EditWindow closes.

        :param change: If the arrays should get updated.
        :param iv_dict: The data structure containing the entries
        :param new_ion: New ion name
        :param natom: new number of atoms
        :param nr: new number of regions
        :param atoms: names of the atoms
        :param regions: names of the regions

        """
        # re-enable this window
        self.root.deiconify()
        # if something has changed
        if change:
            # call the update method to re-size and re-fill the arrays
            self.update_all_iv_arrays(iv_dict, natom, nr)

            # write the ion name in the corresponding entries
            # (see open_edit_material_window())
            # material names are already in the iv_dict
            # switch ATOM and REGION with corresponding name
            for tab_num, tab_name in enumerate(self.nb.tabs()):
                tab_frame = self.nb.nametowidget(tab_name)
                scroll_frame = tab_frame.scroll_frame

                # writing the atom name in it's entry
                if tab_num == 2:
                    content_frame_entry = scroll_frame.content_frame_entry

                    for child in content_frame_entry.winfo_children():
                        if "entry8" in str(child):
                            child["state"] = 'normal'
                            child.delete(0, "end")
                            child.insert(0, str(new_ion))
                            child["state"] = 'disabled'

                # iterate over every ivarray and change
                # ATOM and REGION with the corresponding name
                for iv_num, ivarray in enumerate(scroll_frame.get_ivarrays()):
                    # skip these 2 ivarrays, because
                    # they are arrays that hold the names
                    if (tab_num == 1 and iv_num == 3) \
                            or (tab_num == 3 and iv_num == 1):
                        for child in ivarray.winfo_children():
                            if "entry" in str(child):
                                child["state"] = 'disabled'
                        continue

                    # check for labels with ATOM or REGION in it
                    # and write the correct name in them
                    for child in ivarray.winfo_children():
                        if "label" in str(child):
                            if "ATOM" in child["text"]:
                                index = int(child["text"].split(' ')[-1])
                                if index > 0:
                                    child["text"] = atoms[index - 1]
                            if "REGION" in child["text"]:
                                index = int(child["text"].split(' ')[-1])
                                if index > 0:
                                    child["text"] = regions[index - 1]

    def get_data_from_ivarrays(self):
        """
        Gets the data from all IVArrays and stores them in a IVDict dictionary.
        Key is the tab name.

        """
        iv_dict = IVDict()
        for tab_name in self.nb.tabs():
            tab_ivarrays = self.get_ivarrays_from_tab(tab_name)
            ivarray_tab_values = []
            for ivarray in tab_ivarrays:
                values = self.get_data_from_ivarray(ivarray)
                ivarray_tab_values.append(values)
            iv_dict[tab_name] = ivarray_tab_values
        return iv_dict

    def get_data_from_ivarray(self, ivarray):
        """
        Returns all the values and array state as a IVData object

        :param ivarray: IndexVariableArray

        """
        values = ivarray.get_values()
        # settings to re-create the array
        array_settings = values[2]
        size = ivarray.get_size(array_settings[0],
                                array_settings[1],
                                self.nr, self.natom)
        m = size[0]
        n = size[1]
        if type(m) != int:
            m = m.get()
        if type(n) != int:
            n = n.get()

        # points has an extra region
        if "POINTS" in array_settings[0]:
            m += 1

        if type(self.natom) != int:
            natom = self.natom.get()
        else:
            natom = self.natom
        if type(self.nr) != int:
            nr = self.nr.get()
        else:
            nr = self.nr

        data = IVData(ivarray.get_size_string(
            array_settings[0], array_settings[1]),
            natom, nr, values[1], values[2])
        # points doesn't get changed, so it's just saved as it is
        if "POINT" in array_settings[1]:
            data.values = values[0]
        else:
            # save the values in a 2D grid to re-add them easier later
            for i in range(m * n):
                if i % n == 0:
                    data.values.append([])
                data.values[i // n].append(values[0][i + 1])
        return data


if __name__ == '__main__':
    welcome_window = WelcomeWindow()
