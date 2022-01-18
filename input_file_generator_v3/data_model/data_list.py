class DataList:
    """
    List of parameters with their widgets, values, and default values.

    Each parameter is represented by a tuple (par_name, tk_widget,
    widget_variable, default_value), where

    par_name: (str) name of parameter from database
    tk_widget: Tkinter widget (Checkbutton for logical parameters, Entry else)
    widget_variable: (StringVar) Current value of the parameter
    default_value: (str) text from database column 'default value'
    """

    def __init__(self):
        self.data_list = []

    def add(self, par_name, tk_widget, widget_variable, default_value):
        self.data_list.append((par_name, tk_widget, widget_variable,
                               default_value))

    def print(self):
        for data in self.data_list:
            print(data[0], "[", data[1], "]", ":", data[2].get(),
                  "default:", data[3])

    def get_widgets(self, name):
        widgets = []
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
