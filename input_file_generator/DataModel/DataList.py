class DataList:
    """
    DataList contains one list with tuples where a tuple has the
    following format:

    (PARAMETER_NAME, TKINTER_WIDGET [Entry/Checkbutton], WIDGET_VARIABLE)

    PARAMETER_NAME:      name of parameter from database
                         type:   str
    TKINTER_WIDGET:     Checkbutton for logical parameters, Entry else
    WIDGET_VARIABLE:    contains the current value of the parameter
                        type:   StringVar
    DEFAULT_VALUE:      text from database column 'default value'
                        type:   str
    """

    def __init__(self):
        self.data_list = list()

    def add(self, par_name, tk_widget, widget_variable, default_value):
        self.data_list.append((par_name, tk_widget, widget_variable,
                               default_value))

    def print(self):
        for data in self.data_list:
            print(data[0], "[", data[1], "]", ":", data[2].get(),
                  "default:", data[3])

    def length(self):
        return len(self.data_list)

    def get_widgets(self, name):
        widgets = list()
        for data in self.data_list:
            if name.lower() == data[0].lower():
                widgets.append(data[1])
        return widgets

    def get_variable(self, name):
        for data in self.data_list:
            if name.lower() == data[0].lower():
                return data[2]
        return None

    def get_default_value(self, name):
        for data in self.data_list:
            if name.lower() == data[0].lower():
                return data[3]
        return None
