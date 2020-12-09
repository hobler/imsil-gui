import platform

#from DataModel.Table.DatabaseTable import DatabaseTable
from DataModel.read_sqlite import DatabaseTable
from UI.Frames.scroll_frame import ScrollFrame
from UI.Frames.blanc_frame import BlancFrame

OS = platform.system()


class TabFrame(BlancFrame):
    """        
    TabFrame contains all widgets for a notebook tab.

    Note that a tab in the GUI presents the parameters of one IMSIL "record".
    TabFrame contains a ScrollFrame which contains the widgets for the
    parameters. The Scrollframe allows to scroll up and down the parameter
    list in case the window does not provide enough space for all of them.
    """
    def __init__(self, parent, db_file, table_name, type_of_simulation, 
                 nr, natom, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Get data from database and regroup them
        self.db_table = DatabaseTable(db_file, table_name)
        self.db_table.regroup()
        
        # Create a Scrollframe specifically developed for this project
        self.scroll_frame = ScrollFrame(self, nr, natom)

        # Add parameters to the Scrollframe
        table_rows = self.db_table.get_rows()
        for table_row in table_rows:
            self.add_parameter(table_row)

    def add_parameter(self, table_row):
        """
        Add a parameter to the Scrollframe.

        :param table_row: the row holding all data of the parameter to be added
        """
        par_name = self.db_table.get_name(table_row)
        self.scroll_frame.add_parameter(
            par_name=par_name,
            index_var_list=self.db_table.get_index_vars_for_par(par_name),
            default_value=self.db_table.get_default_value(table_row),
            short_desc=self.db_table.get_short_desc(table_row),
            long_desc=self.create_info_button_text(table_row),
            is_bool=self.db_table.is_logical(table_row),
            is_index_var=self.db_table.is_index_var(table_row))

    def create_info_button_text(self, table_row):
        """
        Create the info message text.
        
        Create a string, which contains all information that should be
        shown to the user when the user presses the info Button.
        
        :param table_row: the row holding all data of the parameter for
                          which the info text should be added
        """
        return (self.db_table.get_long_desc(table_row).rstrip()
                + "\n\n"
                + "Type: " + self.db_table.get_type(table_row).rstrip() 
                + "\n\n" 
                + "Default value: " 
                + self.db_table.get_default_value(table_row).rstrip() 
                + "\n\n" 
                + "Range: " + self.db_table.get_range(table_row).rstrip())
