import platform

from DataModel.Table.DatabaseTable import DatabaseTable
from UI.Frames.scroll.imsil_scroll_frame import ImsilScrollFrame
from UI.Frames.blanc.blanc_frame import BlancFrame

OS = platform.system()


class DbFrame(BlancFrame):
    """        
    DbFrame is a Frame, which contains an ImsilScrollFrame to display
    the parameters.
    """
    def __init__(self, parent, db_file, table_name, type_of_simulation, 
                 nr, natom, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Get data from database
        self.db_table = DatabaseTable(db_file, table_name)
        self.table_rows = self.db_table.get_rows()
        
        # Create a Scrollframe specifically developed for this project
        self.scroll_frame = ImsilScrollFrame(self, nr, natom)

        # Regroup the parameters
        self.table_rows = self.db_table.regroup(self.table_rows)
        
        # Add parameters to the Scrollframe
        for table_row in self.table_rows:
            self.add_parameter(table_row)

    def add_parameter(self, table_row):
        """
        Add a parameter to the Scrollframe.
        
        :param table_row: the row holding all data of the parameter to
                          be added
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
        return ("Description:\n\n" 
                + self.db_table.get_long_desc(table_row).rstrip() 
                + "\n\n"
                + "Type: " + self.db_table.get_type(table_row).rstrip() 
                + "\n\n" 
                + "Default value: " 
                + self.db_table.get_default_value(table_row).rstrip() 
                + "\n\n" 
                + "Range: " + self.db_table.get_range(table_row).rstrip())
