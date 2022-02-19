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

        :param gui_object: the gui object

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
                value = self.gui_object.get_ivdata()
            else:
                value = self.gui_object.get()
        else:
            return None
