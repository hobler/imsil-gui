import tkinter as tk
import platform

from DataModel.DataList import DataList
from DataModel.Table.DatabaseTable import *
from UI.Frames.scroll.imsil_scroll_frame import ImsilScrollFrame
from UI.Frames.blanc.blanc_frame import BlancFrame

OS = platform.system()


def create_info_button_text(table_row):
    """
        create_info_button_text create a string which contains all
        information that should be shown to the user by pressing the info
        button

    :param table_row:
    :return:
    """
    return "Description:\n\n" + get_long_desc(table_row).rstrip() + "\n\n"\
           "Type:\n\n" + get_type(table_row).rstrip() + "\n\n"\
           "Default value:\n\n" + get_default_value(table_row).rstrip() +\
           "\n\nRange:\n\n" + get_range(table_row).rstrip()


class DbFrame(BlancFrame):
    """
        DbFrame is a Frame which contains a ImsilScrollFrame.
        With ImsilScrollFrame you can add parameters
    """

    def __init__(self, parent, db_file, table_name, type_of_simulation,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # get data from database
        self.db_table = DatabaseTable(db_file, table_name).get_table()
        self.index_var_list = get_all_index_vars(self.db_table)
        self.basic_table_rows = get_basics(self.db_table)
        self.advanced_table_rows = get_advanced(self.db_table)

        # create a scrollframe specifically developed from this project
        self.scroll_frame = ImsilScrollFrame(self, self.index_var_list)

        # add parameters to the scrollframe
        for table_row in self.basic_table_rows:
            self.add_parameter(table_row, True)
        for table_row in self.advanced_table_rows:
            self.add_parameter(table_row, False)

    def add_parameter(self, table_row, is_bool):
        par_name = get_name(table_row)
        self.scroll_frame.add_parameter(
            par_name=par_name,
            index_var_list=get_index_vars_for_par(self.db_table, par_name),
            default_value=get_default_value(table_row),
            short_desc=get_short_desc(table_row),
            long_desc=create_info_button_text(table_row),
            is_bool=is_logical(table_row),
            is_basic=is_bool
        )
