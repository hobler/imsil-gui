from data_model.read_sqlite import DatabaseTable
from UI.frames.scroll_frame import ScrollFrame
from UI.frames.blanc_frame import BlancFrame


class TabFrame(BlancFrame):
    """
    TabFrame contains all widgets for a notebook tab.

    Note that a tab in the GUI presents the parameters of one IMSIL "record".
    Note that a tab in the GUI presents the parameters of one IMSIL "record".
    TabFrame contains a ScrollFrame which contains the widgets for the
    parameters. The ScrollFrame allows to scroll up and down the parameter
    list in case the window does not provide enough space for all of them.
    """
    def __init__(self, parent, db_file, table_name, type_of_simulation,
                 nr, natom, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Get the database table and regroup the parameters
        self.db_table = DatabaseTable(db_file, table_name)
        self.db_table.regroup()

        # Create a ScrollFrame specifically developed for this project
        self.scroll_frame = ScrollFrame(self, nr, natom)

        # Add parameters to the ScrollFrame
        for table_row in self.db_table:
            self.add_parameter(table_row)

    def add_parameter(self, table_row):
        """
        Add a parameter to the ScrollFrame.

        :param table_row: the row holding all data of the parameter to be added
        """
        self.scroll_frame.add_parameter(
            par_name=table_row.get_name(),
            index_var_list=table_row.get_index_vars(),
            default_value=table_row.get_default_value(),
            short_desc=table_row.get_short_desc(),
            long_desc=self.create_info_button_text(table_row),
            is_bool=table_row.is_logical(),
            is_index_var=table_row.is_index_var())

    def get_ivarrays(self):
        """
        Returns the IndexVariableArrays that are placed inside this Tab_Frame.

        """
        return self.scroll_frame.get_ivarrays()

    def clear_ivarray_list(self):
        """
        Clears the ivarray_list in the scroll_frame.

        """
        self.scroll_frame.clear_ivarray_list()

    @staticmethod
    def create_info_button_text(table_row):
        """
        Create the info message text for a parameter.

        Create a string, which contains all information that should be
        shown to the user when the user presses the info Button.

        :param table_row: The row holding all data of the parameter.
        """
        return (table_row.get_long_desc().rstrip()
                + "\n\n"
                + "Type: " + table_row.get_type().rstrip()
                + "\n\n"
                + "Default value: "
                + table_row.get_default_value().rstrip()
                + "\n\n"
                + "Range: " + table_row.get_range().rstrip())
