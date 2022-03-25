import tkinter as tk


class CheckbuttonArray(tk.Frame):
    """
    Class that defines an array of Checkbuttons as widget.
    Used for the parameters FREEX and FREEZ.

    Contains a list of Checkboxes and functions to access and set the
    values accordingly.
    """

    def __init__(self, parent, n, default_value, value, **kw):
        """

        :param parent: parent frame
        :param n: number of checkboxes
        :param default_value: default value in the format "(T/F,T/F,...)"
        :param value: current value in the format "(T/F,T/F,...)"
        """

        super().__init__(parent, **kw)

        self.rowconfigure(0, weight=1)

        self.checkboxes = []
        self.cb_vars = []
        for i in range(n):
            self.columnconfigure(i, weight=1)
            cb_string_var = tk.StringVar()
            checkbutton = tk.Checkbutton(self, text="",
                                         variable=cb_string_var,
                                         onvalue="T",
                                         offvalue="F")
            checkbutton.grid(row=0, column=i)
            self.checkboxes.append(checkbutton)
            self.cb_vars.append(cb_string_var)

        self.set(value if value is not None else default_value)

    def set(self, value):
        """
        Set the currently displayed value.

        :param value: value in the format "(T/F,T/F,...)"
        """
        if value is not None:
            if len(value) >= 5:
                values = value[1:-1].split(",")
                if len(values) == len(self.checkboxes):
                    for i in range(len(values)):
                        self.cb_vars[i].set(values[i])

    def get(self):
        """
        Get the currently displayed value.

        :returns: value in the format "(T/F,T/F,...)"
        """
        values = []
        for i in range(len(self.cb_vars)):
            values.append(self.cb_vars[i].get())

        result = "(" + ",".join(values) + ")"
        return result
