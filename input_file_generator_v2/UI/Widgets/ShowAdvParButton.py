from enum import Enum
from tkinter import ttk

from UI.Frames.blanc.blanc_frame import BlancFrame


class ButtonState(Enum):
    SHOW_BASICS = 1
    SHOW_ALL = 2


class ShowAdvParButton(BlancFrame):
    """
    Frame that contains a special Button for extending and collapsing widgets
    in a frame.

    It also includes a state that can be read by the state attribute or with
    the Support of the functions is_state_show_basic and is_state_show_all. To
    toggle the state the function toggle_state can be used.
    """

    def __init__(self, parent, button_text="",
                 init_state=ButtonState.SHOW_ALL, *args, **kwargs):
        super().__init__(parent, rows=1, columns=1, *args, **kwargs)
        self.state = init_state
        style = ttk.Style()
        style.configure('AdvButton.TButton', font=('calibri', 15, 'bold'),
                        borderwidth='4')
        style.map('AdvButton.TButton',
                  foreground=[('active', '!disabled', 'black')],
                  background=[('active', 'black')])
        self.button = ttk.Button(self, text=button_text,
                                 style='AdvButton.TButton')
        self.button.grid(row=0, column=0, sticky="NESW")

    def toggle_state(self):
        if self.state is ButtonState.SHOW_BASICS:
            self.state = ButtonState.SHOW_ALL
        else:
            self.state = ButtonState.SHOW_BASICS

    def is_state_show_basic(self) -> bool:
        return self.state is ButtonState.SHOW_BASICS

    def is_state_show_all(self) -> bool:
        return self.state is ButtonState.SHOW_ALL
