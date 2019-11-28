from UI.Frames.blanc.blanc_frame import BlancFrame
from UI.Frames.scroll.imsil_scroll_frame import ImsilScrollFrame


class TestScrollFrame(BlancFrame):
    """
    class for the start frame
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.sf = ImsilScrollFrame(self, columns=2)

        for i in range(50):
            label_entry = self.sf.add_Label_Entry(
                label_text="LabelEntry " + str(i))
            label_entry.grid(row=i, column=0, sticky="NESW")
            label_entry = self.sf.add_Label_Entry(
                label_text="LabelEntry " + str(i) + "a")
            label_entry.grid(row=i, column=1, sticky="NESW")



