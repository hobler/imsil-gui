"""
    Utility module for often used static functions
"""
import Pmw


def center_window(tk_window):
    """
    Place the given Tk window in the center of the screen.

    :param tk_window: a window of type tk.Tk
    """
    # Hide widget
    tk_window.withdraw()
    # Update "requested size" from geometry manager
    tk_window.update_idletasks()

    # Get the requested values of the width and height
    window_width = tk_window.winfo_reqwidth()
    window_height = tk_window.winfo_reqheight()

    # Calculate the position of the upper left corner of the window
    pos_x = int(tk_window.winfo_screenwidth() / 2 - window_width / 2)
    pos_y = int(tk_window.winfo_screenheight() / 2 - window_height / 2)

    # Center the window
    tk_window.geometry("+{}+{}".format(pos_x, pos_y))
    # Show widget
    tk_window.deiconify()


def get_size_string(par_name, index_var_list):
    """
    Returns the width and height of the grid as a list
    depending on the variables to display.

    For example an IVArray with dimension of 1 and
    ATOM as index variable returns ["1", "a"].
    Whereas a dimension of 2 containing an atom and a region returns ["r", "a"].

    For the parameter POS this function returns ["0", "0"]

    :param par_name: Parameter Name.
    :param index_var_list: Index Variable List.

    :return: With and height of the grid as a list. [1/a/r, 1/a/r]
    """
    size = ["0", "0"]

    dim = len(index_var_list)
    if dim == 1:
        if ("ATOM1" in index_var_list or "ATOM2" in index_var_list or
                "ATOM" in index_var_list):
            # 1 x NATOM array
            size = ["1", "a"]
        elif ("REGION" in index_var_list and
              # POINTS in parameter name
              "POINTS" in par_name):
            # NR x 1 array
            size = ["r", "1"]
        elif "REGION" in index_var_list:
            # 1 x NR array
            size = ["1", "r"]
    elif dim == 2:
        if ("REGION" in index_var_list and
                ("ATOM1" in index_var_list or
                 "ATOM2" in index_var_list)):
            # NR x NATOM array
            size = ["r", "a"]
        elif "ATOM1" in index_var_list and "ATOM2" in index_var_list:
            # NATOM x NATOM array
            size = ["a", "a"]

    return size


def create_info_button_text(parameter_entry):
    """
    Create the info message text for a parameter.

    Create a string, which contains all information that should be
    shown to the user when the user presses the info Button.

    :param parameter_entry: The ParameterEntry holding
    all data of the parameter.
    """
    return (parameter_entry.get_long_desc().rstrip()
            + "\n\n"
            + "Type: " + parameter_entry.get_type().rstrip()
            + "\n\n"
            + "Default value: "
            + parameter_entry.get_default_value().rstrip()
            + "\n\n"
            + "Range: " + parameter_entry.get_range().rstrip())


def create_tooltip(parent, widget, text):
    balloon = Pmw.Balloon(parent)
    balloon.bind(widget, text)
