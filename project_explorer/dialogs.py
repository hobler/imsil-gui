#!/usr/bin/python3
"""
Provide simple dialogs that are required for the ProjectExplorer class.

The dialog implementations were not subclassed from Dialog but rather
re-implemented to provide specific appearance and functionality that was
different from the one forced from the superclass.
"""
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Frame, Label, Entry
from tkinter.constants import LEFT, END, SUNKEN, RAISED, NORMAL, DISABLED
from pathlib import PurePath, Path


class NewButtonDialog(tk.Toplevel):
    """
    Simple two-button dialog for creating a new .inp file.

    The dialog provides two button for either creating a new empty .inp
    file or for copying an existing .inp file.
    """

    def __init__(self, master, new_file_dir: Path):
        """
        Initializes a simple two_button dialog that is shown when the user
        clicks the "New" button on the project explorer.

        Args:
            master:
                Parent of the dialog, here the project explorer window.
            new_file_dir:
                Path of the directory for the new .inp file

        """
        super().__init__(master)
        self.master = master
        self.new_file_dir = new_file_dir
        self.withdraw()
        if master is not None and master.winfo_viewable():
            self.transient(master)

        self.title = "Please choose an action:"
        self.box = None
        self.result = None
        self.initial_focus = self.body()
        self.new_file_button = None
        self.copy_file_button = None
        self.button_box()
        self.entry_label = None
        self.entry: Entry = None
        self.confirm_button: tk.Button = None

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if master is not None:
            self.geometry(f"+{master.winfo_rootx() + 50}+"
                          f"{master.winfo_rooty() + 50}")

        self.deiconify()  # Make window visible
        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def destroy(self):
        """Destroys the window."""
        self.initial_focus = None
        super().destroy()

    def body(self):
        """Creates the dialog's body."""
        self.box = Frame(self, height=0, width=300, borderwidth=2,
                         relief="groove")
        prompt_label = Label(self.box, text=" Please choose an action:",
                             font=("Segoe UI", 12, "bold"))
        prompt_label.grid(column=0, row=0, columnspan=2, sticky="nswe")
        self.bind("<Escape>", self.cancel)
        self.box.pack(padx=0, pady=0)
        return self.box

    def button_box(self):
        """
        Adds the button_box to the dialog.

        One button asks for a filename string and then assigns it to the
        "result" attribute. The other button opens the native file dialog and
        asks for a .inp file to be selected so that it will eventually be
        copied, the file path is then assigned to the "result" attribute.
        """
        self.new_file_button = tk.Button(self.box, text="Create new Project",
                                    command=self.ask_string)
        self.copy_file_button = tk.Button(self.box, text="Copy Existing Project",
                                     command=self.copy_project)
        self.new_file_button.grid(column=0, row=1, sticky="nswe")
        self.copy_file_button.grid(column=1, row=1, sticky="nswe")

    def finalize(self):
        """Takes care of window management and then closes the dialog."""
        self.withdraw()
        self.update_idletasks()
        try:
            return self.result
        finally:
            self.cancel()

    def cancel(self):
        """Handles the window cleanup when the user closes the dialog without
        performing an action."""
        # put focus back to the master window
        if self.master is not None:
            self.master.focus_set()
        self.destroy()

    def new_file(self):
        """
        Handle the request of a filename for a new .inp file

        Since the existence of a project is uniquely defined by the
        corresponding .inp file, an .inp file will be created.
        """
        name_string = ""
        name_string = self.entry.get()
        if name_string is not None and name_string != "":
            name_string = filename_fix_existing(self.new_file_dir, name_string)
            self.result = name_string
            self.finalize()

    def ask_string(self):
        """Create an Entry widget on the dialog window"""

        self.entry_label = Label(self, text="Please type a project name",
                                 justify=LEFT)
        self.entry_label.pack()
        self.new_file_button.config(relief=SUNKEN)
        self.new_file_button.config(state=DISABLED)
        self.entry = Entry(self, name="entry")
        self.entry.pack()

        self.entry.insert(0, "Project Name")
        self.entry.select_range(0, END)
        self.confirm_button = tk.Button(self, text="Confirm",
                                    command=self.new_file)
        self.confirm_button.pack()

    def copy_project(self):
        """Handles the request of a .inp file from the native file dialog."""
        if self.entry is not None:
            self.entry.destroy()
            self.confirm_button.destroy()
            self.entry_label.destroy()
            self.new_file_button.config(relief=RAISED)
            self.new_file_button.config(state=NORMAL)
        file_name = None
        file_name = askopenfilename(filetypes=[("Input Files", ".inp")])
        if file_name is None or str(file_name) == "." or file_name == "":
            return
        self.result = PurePath(file_name)
        self.finalize()

def filename_fix_existing(new_file_dir, filename) -> str:
    """
    Expand name portion of filename with numeric '(x)' suffix to
    return filename that doesn't exist already.

    This function accepts either the filename:str or the filepath:Purepath
    as its filename argument.
    """
    dirname = new_file_dir
    if type(filename) == str:
        name, ext = filename, "inp"
    elif isinstance(filename, PurePath):
        parent = filename.parent
        name, ext = str(filename.name).rsplit('.', 1)
    names = [x for x in os.listdir(dirname) if x.startswith(name)]
    names = [x.rsplit('.', 1)[0] for x in names]
    suffixes = [x.replace(name, '') for x in names]
    # filter suffixes that match ' (x)' pattern
    suffixes = [x[1:-1] for x in suffixes
                if x.startswith('(') and x.endswith(')')]
    indexes = [int(x) for x in suffixes
               if set(x) <= set('0123456789')]
    idx = 0
    if indexes:
        idx += sorted(indexes)[-1]
    if not indexes and names:
        idx = 1
    if idx == 0:
        idx = ""
    else:
        idx = f"({idx+1})"
    if isinstance(filename, PurePath):
        return str(os.path.join(parent,f"{name}{idx}.{ext}"))
    return f"{name}{idx}.{ext}"

