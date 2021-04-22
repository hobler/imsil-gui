"""
    Utility module for often used static functions
"""


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
