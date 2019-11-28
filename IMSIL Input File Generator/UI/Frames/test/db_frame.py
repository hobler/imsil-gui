import tkinter as tk
import platform

from DataModel.DataList import DataList
from DataModel.Table.DatabaseTable import *
from UI.Frames.scroll.imsil_scroll_frame import ImsilScrollFrame
from UI.Frames.blanc.blanc_frame import BlancFrame

OS = platform.system()


class DbFrameV1(BlancFrame):
    """
    class for a frame that represent a database table
    """

    def __init__(self, parent, db_file, table_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.scroll_frame = ImsilScrollFrame(self, columns=3)

        # fill scroll frame with data
        self.ui_data_list = DataList()
        self.db_table = DatabaseTable(db_file, table_name).get_table()

        # get all logical parameter names that occures in the defualt values
        self.obligatory_pars = get_obligatory_if_list(self.db_table)

        # import all not logical entries that not depend on a flag
        for db_row in self.db_table:
            item_name = get_name(db_row)
            item_type = get_type(db_row)
            default_value = get_default_value(db_row)
            if item_name not in self.obligatory_pars and \
                    not is_obligatory_if(default_value) and \
                    "logical" not in item_type:
                # add label with parameter name as text
                if has_comment(default_value):
                    self.add_Label_Entry(label_text=item_name,
                                         entry_text="")
                else:
                    self.add_Label_Entry(label_text=item_name,
                                         entry_text=default_value)

        # import all logical entries that not depend on a flag
        offset = self.ui_data_list.length()
        for db_row in self.db_table:
            item_name = get_name(db_row)
            item_type = get_type(db_row)
            default_value = get_default_value(db_row)
            if item_name not in self.obligatory_pars and \
                    not is_obligatory_if(default_value) and \
                    "logical" in item_type:
                # add chackbox for logical parameter
                self.add_Check_buttons(cb_text=item_name,
                                       cb_var_value=default_value,
                                       grid_row_offset=offset,
                                       grid_column=1)

        # import all logical entries and put all entries that depend on the
        # flag under the depending flag
        offset = self.ui_data_list.length()
        for obligatory_item_name in self.obligatory_pars:
            # add chackbox for logical parameter
            cb_default_value = get_default_value_for_name(
                self.db_table,
                obligatory_item_name)
            self.add_Check_buttons(cb_text=obligatory_item_name,
                                   cb_var_value=cb_default_value,
                                   grid_row_offset=offset,
                                   grid_column=2, padx=0)
            for db_row in self.db_table:
                item_name = get_name(db_row)
                default_value = get_default_value(db_row)
                # if obligatory_item_name in default_value:
                    # add label with parameter name as text

    def cb_command(self, name):
        for ui_data in self.ui_data_list.data_list:
            if name in ui_data[0]:
                print(ui_data[0], ui_data[2].get())

        value = self.ui_data_list.get_variable(name)
        if value is not None:
            print("CheckButton ", name, " set to ", value.get())

        obligatory_if = str(name + "=" + value.get())
        for setup_row in self.db_table:
            item_name = get_name(setup_row)
            default_value = get_default_value(setup_row)
            if obligatory_if in default_value:
                widgets = self.ui_data_list.get_widgets(item_name)
                for widget in widgets:
                    widget.entry.config(state='normal')
            elif name in default_value:
                widgets = self.ui_data_list.get_widgets(item_name)
                for widget in widgets:
                    widget.entry.config(state='disabled')

    def get_ui_data_list(self):
        return self.ui_data_list
