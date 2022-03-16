from data_model.iv_data import IVDict, IVData
from utility import get_size_string


class ParameterData:
    """
    This data structure stores all of the necessary parameters
    that are defined in the SQLite Database.

    It is used to create the Parameter Editor Window and the Edit Window.

    Data is stored per tab as a list of ParameterEntries.
    Tabs are stored in a dict object accessed by the tab name.

    """
    def __init__(self, db_tables):
        """
        Init function of ParameterData.
        Creates the data structure and fills it with default values.

        :param db_tables: List of DatabaseTable objects. Individual
        DatabaseTable objects should be regrouped before passing the
        list to this data structure. (db_table.regroup())

        """
        self.tab_dict = {}

        # loop through every database table and add the table entries to
        # the list of entries in each tab
        for db_table in db_tables:
            self.tab_dict[db_table.table_name] = []
            for db_table_row in db_table:
                # add a new parameter entry to the tab
                self.tab_dict[db_table.table_name].append(
                    ParameterEntry(name=db_table_row.get_name(),
                                   desc_short=db_table_row.get_short_desc(),
                                   desc_long=db_table_row.get_long_desc(),
                                   p_type=db_table_row.get_type(),
                                   default_value=db_table_row.get_default_value(),
                                   p_range=db_table_row.get_range(),
                                   basic=db_table_row.get_basic(),
                                   index_vars=db_table_row.get_index_vars(),
                                   is_logical=db_table_row.is_logical(),
                                   is_index_var=db_table_row.is_index_var()))

    def __getitem__(self, key):
        """
        Allows to access each tab_dict entry directly with the [] operator

        :param key: tab_name

        """
        return self.tab_dict[key]

    def __iter__(self):
        """
        Used to make the object iterable. Returns an iteration over the tab_dict.

        """
        return iter(self.tab_dict)

    def __next__(self):
        """
        Used to make the object iterable. Returns an iteration over the tab_dict.

        """
        return next(self.tab_dict)

    def get_entry(self, tab_name, param_name):
        """
        Returns the ParameterEntry corresponding to the tab and name.

        :param tab_name: name of the tab as defined in the database
        :param param_name: name of the parameter as defined in the database

        """
        for p_entry in self.tab_dict[tab_name]:
            if p_entry.name == param_name:
                return p_entry

    def get_entry_value(self, tab_name, param_name):
        """
        Returns the value of the ParameterEntry corresponding to the tab and name.

        :param tab_name: name of the tab as defined in the database
        :param param_name: name of the parameter as defined in the database

        """
        entry = self.get_entry(tab_name, param_name)
        return entry.get_value()

    def set_entry_value(self, tab_name, param_name, value):
        """
        Sets the value of the ParameterEntry corresponding to the tab and name.

        :param tab_name: name of the tab as defined in the database
        :param param_name: name of the parameter as defined in the database
        :param value: value to be set in the entry

        """
        entry = self.get_entry(tab_name, param_name)
        return entry.set_value(value)

    def get_nr(self):
        """
        Returns the NR parameter.

        """
        return self.get_entry_value("setup", "NR")

    def get_natom(self):
        """
        Returns the NATOM parameter.

        """
        return self.get_entry_value("setup", "NATOM")

    def get_materials(self):
        """
        Returns the material names as a list of strings.

        """
        if type(self.get_entry_value("material", "NAME")) == IVData:
            return self.get_entry_value("material", "NAME").to_list()
        else:
            return []

    def get_atoms(self):
        """
        Returns the atom names as a list of strings.

        """
        if type(self.get_entry_value("atoms", "NAME")) == IVData:
            return self.get_entry_value("atoms", "NAME").to_list()
        else:
            return []

    def to_iv_dict(self):
        """
        Creates an IVDict object for using the edit_window.py

        :returns: IVDict containing the currently stored values

        """
        iv_dict = IVDict()
        for tab_name in self:
            iv_dict[tab_name] = self.get_ivdata_list_from_tab(tab_name)
        return iv_dict

    def load_from_iv_dict(self, iv_dict):
        """
        Loads the IVData objects of the IVDict in the current_value
        property of each iv_array parameter_entry.

        :param iv_dict: IVDict containing the values to store

        """
        for tab_name in self:
            for entry in iv_dict[tab_name]:
                entry_name = entry.array_settings[0]
                self.set_entry_value(tab_name, entry_name, entry)

    def get_ivdata_list_from_tab(self, tab_name):
        """
        Returns every iv array as an IVData object list.

        :param tab_name: name of the tab

        """
        iv_data_list = []

        for param_entry in self[tab_name]:
            if param_entry.get_is_index_var():
                # if the parameter is an iv array, append the IVData
                iv_data_list.append(param_entry.current_value)
        return iv_data_list

    def readout_parameter_editor(self):
        """
        Reads every parameter from the gui and
        stores it in its current_value property.
        Should only be used when parameter editor is open.

        """
        for tab_name in self:
            for param_entry in self[tab_name]:
                param_entry.readout_gui()

    def add_atom(self):
        """
        Adds an Atom to every Entry
        """
        for tab in self:
            # for all index variable arrays in that tab
            for p_entry in self[tab]:
                p_entry.add_atom()

    def add_region(self):
        """
        Adds a Region to every Entry
        """
        for tab in self:
            # for all index variable arrays in that tab
            for p_entry in self[tab]:
                p_entry.add_region()

    def add_atom_at(self, index):
        """
        Adds an Atom to every Entry at a given position

        :param index: index
        """
        for tab in self:
            # for all index variable arrays in that tab
            for p_entry in self[tab]:
                p_entry.add_atom_at(index)

    def add_region_at(self, index):
        """
        Adds a Region to every Entry at a given position

        :param index: index
        """
        for tab in self:
            # for all index variable arrays in that tab
            for p_entry in self[tab]:
                p_entry.add_region_at(index)

    def remove_atom(self, index):
        """
        Removes an Atom from every Entry at a given position

        :param index: index
        """
        for tab in self:
            # for all index variable arrays in that tab
            for p_entry in self[tab]:
                p_entry.remove_atom(index)

    def remove_region(self, index):
        """
        Removes a Region from every Entry at a given position

        :param index: index
        """
        for tab in self:
            # for all index variable arrays in that tab
            for p_entry in self[tab]:
                p_entry.remove_region(index)

    def swap_atom(self, index_1, index_2):
        """
        Swap the contents of the atoms at index 1 and 2

        :param index_1: index of the first atom
        :param index_2: index of the second atom
        """
        for tab in self:
            # for all index variable arrays in that tab
            for p_entry in self[tab]:
                p_entry.swap_atom(index_1, index_2)

    def swap_region(self, index_1, index_2):
        """
        Swap the contents of the regions at index 1 and 2

        :param index_1: index of the first regions
        :param index_2: index of the second regions
        """
        for tab in self:
            # for all index variable arrays in that tab
            for p_entry in self[tab]:
                p_entry.swap_region(index_1, index_2)

    def set_material_name_at(self, index, name):
        """
        Sets the material name at the given index

        :param index: index of the material
        :param name: material name
        """
        mat_name_ivdata = self.get_entry_value("material", "NAME")
        mat_name_ivdata.values[0][index] = name


class ParameterEntry:
    """
    This data structure stores all of the necessary data for a single parameter.

    """
    def __init__(self, name, desc_short, desc_long, p_type, default_value,
                 p_range, basic, index_vars, is_logical, is_index_var):
        """
        Init function of ParameterEntry.

        """
        self.name = name
        self.desc_short = desc_short
        self.desc_long = desc_long
        self.p_type = p_type
        self.default_value = default_value
        self.p_range = p_range
        self.basic = basic

        self.index_vars = index_vars
        self.is_logical = is_logical
        self.is_index_var = is_index_var

        # can be boolean (logical), string or similar (entry)
        # or IVData (Index Variable Array)
        self.current_value = default_value

        # insert new, empty IVData with minimum size
        if self.get_is_index_var():
            self.current_value = IVData(size_string=
                                        get_size_string(self.name,
                                                        self.index_vars),
                                        natom=2, nr=1,
                                        array_state=(False, False),
                                        array_settings=(self.name,
                                                        self.index_vars,
                                                        self.default_value,
                                                        self.desc_short,
                                                        self.desc_long))
            # fill empty values
            if "POINT" in self.index_vars:
                self.current_value.values = ['', '']
            else:
                # save the values in a 2D grid
                # to re-add them easier later
                m = self.current_value.get_m()
                n = self.current_value.get_n()
                for i in range(m * n):
                    if i % n == 0:
                        self.current_value.values.append([])
                    self.current_value.values[i // n].append("")

        # stores a reference to the gui entry object in the parameter editor
        # that represents this parameter. Used to get the current value easier
        # after editing the parameters easier without looping over every gui
        # object.
        # - entries are accessed by entry.get()
        # - logical is accessed by calling get() on the associated variable
        #   which is stored as the gui object
        # - ivarray data is accessed by calling get_ivdata() on it
        self.gui_object = None

    def get_value(self):
        """
        Returns the current value stored in the parameter.

        """
        return self.current_value

    def set_value(self, value):
        """
        Sets the currently stored value.

        :param value: the value that's going to be saved

        """
        self.current_value = value

    def set_gui_object(self, gui_object):
        """
        Sets the reference to the gui object associated with this entry.
        Has to be called for each entry when building the GUI.

        :param gui_object: the gui object (entry, checkbutton, iv_Array)

        """
        self.gui_object = gui_object

    def read_value_from_gui(self):
        """
        Reads and returns the value(s) written in the gui object.

        logical returns "T" or "F"
        entry returns string
        index_var_array returns IVData

        """
        if self.gui_object is not None:
            if self.is_index_var:
                return self.gui_object.get_ivdata()
            else:
                return self.gui_object.get()
        else:
            return None

    def readout_gui(self):
        """
        Sets current value to the value written in the gui.
        Used when closing the parameter editor.

        """
        self.current_value = self.read_value_from_gui()

    def get_name(self):
        """Return the name of the parameter."""
        return self.name

    def get_short_desc(self):
        """Return the short description of the parameter."""
        return self.desc_short

    def get_long_desc(self):
        """Return the long description of the parameter."""
        return self.desc_long

    def get_type(self):
        """Return the type of the parameter."""
        return self.p_type

    def get_default_value(self):
        """Return the default value of the parameter"""
        return self.default_value

    def get_range(self):
        """Return the range of the parameter"""
        return self.p_range

    def get_basic(self):
        """Return the basic flag of the parameter."""
        return self.basic

    def get_index_vars(self):
        """Return a list of index variables for the parameter."""
        return self.index_vars

    def get_is_logical(self):
        """Check if the parameter is a boolean"""
        return self.is_logical

    def get_is_index_var(self):
        """Check if the parameter is an index variable array."""
        return self.is_index_var

    def add_atom(self):
        """
        Adds an Atom to every IVArray
        """
        if self.get_is_index_var():
            if type(self.get_value()) == IVData:
                self.get_value().add_atom()

    def add_region(self):
        """
        Adds a Region to every IVArray
        """
        if self.get_is_index_var():
            if type(self.get_value()) == IVData:
                self.get_value().add_region()

    def add_atom_at(self, index):
        """
        Adds an Atom to every IVArray at a given position

        :param index: index
        """
        if self.get_is_index_var():
            if type(self.get_value()) == IVData:
                self.get_value().add_atom_at(index)

    def add_region_at(self, index):
        """
        Adds a Region to every IVArray at a given position

        :param index: index
        """
        if self.get_is_index_var():
            if type(self.get_value()) == IVData:
                self.get_value().add_region_at(index)

    def remove_atom(self, index):
        """
        Removes an Atom from every IVArray at a given position

        :param index: index
        """
        if self.get_is_index_var():
            if type(self.get_value()) == IVData:
                self.get_value().remove_atom(index)

    def remove_region(self, index):
        """
        Removes a Region from every IVArray at a given position

        :param index: index
        """
        if self.get_is_index_var():
            if type(self.get_value()) == IVData:
                self.get_value().remove_region(index)

    def swap_atom(self, index_1, index_2):
        """
        Swap the contents of the atoms at index 1 and 2

        :param index_1: index of the first atom
        :param index_2: index of the second atom
        """
        if self.get_is_index_var():
            if type(self.get_value()) == IVData:
                self.get_value().swap_atom(index_1, index_2)

    def swap_region(self, index_1, index_2):
        """
        Swap the contents of the regions at index 1 and 2

        :param index_1: index of the first regions
        :param index_2: index of the second regions
        """
        if self.get_is_index_var():
            if type(self.get_value()) == IVData:
                self.get_value().swap_region(index_1, index_2)
