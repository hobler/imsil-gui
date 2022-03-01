from UI.frames.scroll_frame import ScrollFrame
from UI.frames.blanc_frame import BlancFrame


class TabFrame(BlancFrame):
    """
    TabFrame contains all widgets for a notebook tab.

    Note that a tab in the GUI presents the parameters of one IMSIL "record".
    TabFrame contains a ScrollFrame which contains the widgets for the
    parameters. The ScrollFrame allows scrolling up and down the parameter
    list in case the window does not provide enough space for all of them.
    """
    def __init__(self, parent, parameter_list, type_of_simulation,
                 nr, natom, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Get the database table and regroup the parameters
        self.parameter_list = parameter_list

        # Create a ScrollFrame specifically developed for this project
        self.scroll_frame = ScrollFrame(self, nr, natom)

        # Add parameters to the ScrollFrame
        for parameter in self.parameter_list:
            self.add_parameter(parameter)

    def add_parameter(self, parameter_entry):
        """
        Add a parameter to the ScrollFrame.

        :param parameter_entry: the ParameterEntry object to be added
        containing all information about the parameter.
        """
        self.scroll_frame.add_parameter(parameter_entry)

    def get_ivarrays(self):
        """
        Return the IndexVariableArrays that are placed inside this Tab_Frame.
        """
        return self.scroll_frame.get_ivarrays()

    def clear_ivarray_list(self):
        """
        Clear the ivarray_list in the scroll_frame.
        """
        self.scroll_frame.clear_ivarray_list()
