import tkinter as tk
import platform

from DataModel.Table.DatabaseTable import DatabaseTable
from UI.Frames.scroll.imsil_scroll_frame import ImsilScrollFrame
from UI.Frames.blanc.blanc_frame import BlancFrame

OS = platform.system()


class DbFrame(BlancFrame):
    """
    DbFrame is a Frame which contains an ImsilScrollFrame.
    With ImsilScrollFrame you can add parameters
    """

    def __init__(self, parent, db_file, table_name, type_of_simulation,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # get data from database
        self.db_table = DatabaseTable(db_file, table_name)
        self.index_var_list = self.db_table.get_all_index_vars()
        self.basic_table_rows = self.db_table.get_basics()
        self.advanced_table_rows = self.db_table.get_advanced()

        # create a scrollframe specifically developed for this project
        self.scroll_frame = ImsilScrollFrame(self, self.index_var_list)

        # add parameters to the scrollframe
        for table_row in self.basic_table_rows:
            self.add_parameter(table_row, is_basic=True)
        for table_row in self.advanced_table_rows:
            self.add_parameter(table_row, is_basic=False)

    def add_parameter(self, table_row, is_basic):
        """
        Add a parameter to DbFrame
        """
        par_name = self.db_table.get_name(table_row)
        self.scroll_frame.add_parameter(
            par_name=par_name,
            index_var_list=self.db_table.get_index_vars_for_par(par_name),
            default_value=self.db_table.get_default_value(table_row),
            short_desc=self.db_table.get_short_desc(table_row),
            long_desc=self.create_info_button_text(table_row),
            is_bool=self.db_table.is_logical(table_row),
            is_basic=is_basic)

    def create_info_button_text(self, table_row):
        """
        Create a string which contains all information that should be shown to
        the user by pressing the info button
        """
        return "Description:\n\n" + \
               self.db_table.get_long_desc(table_row).rstrip() + "\n\n" \
               "Type:\n\n" + \
               self.db_table.get_type(table_row).rstrip() + "\n\n" \
               "Default value:\n\n" + \
               self.db_table.get_default_value(table_row).rstrip() + "\n\n" \
               "Range:\n\n" + \
               self.db_table.get_range(table_row).rstrip()
