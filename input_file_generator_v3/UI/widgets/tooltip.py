"""
    Utility module for creating tooltip buttons
"""
import os
from tkinter import messagebox

import tkinter as tk

from UI.frames.scroll_frame import INFO_WIDTH, INFO_HEIGHT
from utility import create_info_button_text, create_tooltip


def create_tooltip_btn(parent, parameter_entry):
    """
    Creates an info button that displays a help text when clicked on.
    Text is specified by the description of the parameter_entry.

    :param parent: Parent widget of the button
    :param parameter_entry: ParameterEntry contains the description
    """

    short_desc = parameter_entry.get_short_desc()
    par_name = parameter_entry.get_name()
    long_desc = create_info_button_text(parameter_entry)

    btn_info = create_custom_tooltip_btn(parent, short_desc, par_name,
                                              long_desc)

    return btn_info


def create_custom_tooltip_btn(parent, short_desc, par_name, long_desc):
    """
    Creates a custom info button that displays a help text when clicked on.
    Text is specified by the descriptions.

    :param parent: Parent widget of the button
    :param short_desc: Displayed when hovering the mouse over the button.
    :param par_name: Title of the help text box.
    :param long_desc: Text inside the help text box.
    """

    btn_info = tk.Button(parent, text="Button",
                         width=INFO_WIDTH, height=INFO_HEIGHT)
    if short_desc is not None:
        create_tooltip(btn_info, btn_info, short_desc)
    photo = tk.PhotoImage(file=os.path.join("pics", "info_sign_1.gif"))
    btn_info.config(image=photo)
    btn_info.image = photo
    btn_info.config(takefocus=False)
    btn_info.config(
        command=lambda: messagebox.showinfo(par_name, long_desc))

    return btn_info