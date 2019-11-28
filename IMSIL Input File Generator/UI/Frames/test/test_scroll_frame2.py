import tkinter as tk
from tkinter import ttk

from DataModel.DataList import DataList
from UI.Frames.blanc.blanc_frame import BlancFrame
from UI.Frames.scroll.imsil_scroll_frame import ImsilScrollFrame


class TestScrollFrame2(BlancFrame):
    """
    class for a test scroll frame.

    Load first some basic parameters to the basic frame of the scrollframe.
    Then load some advanced parameters to the advanced frame of the
    scrollframe. Finally run toggle_adv() to show only basic parameters in
    the scrollframe.
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.index_var_list = list(["ATOM1", "ATOM2"])
        # self.index_var_list = list()
        self.sf = ImsilScrollFrame(self, index_var_list=self.index_var_list)
        self.ui_data_list = DataList()

        self.sf.add_parameter(par_name="Test par 1",
                              index_var_list=list(), short_desc="par for test")
        self.sf.add_parameter(par_name="Test parameter 2",
                              index_var_list=list(["ATOM2"]), is_bool=True)
        self.sf.add_parameter(par_name="Test par 31213112",
                              index_var_list=list(["ATOM1", "ATOM2"]))

        for i in range(4, 4):
            self.sf.add_parameter(par_name="Test parameter " + str(i),
                                  is_basic=False)
        self.sf.toggle_adv()
