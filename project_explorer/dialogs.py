#!/usr/bin/python3
"""
Provide simple dialogs that are required for the ProjectExplorer class.

The dialog implementations were not subclassed from Dialog but rather
re-implemented to provide specific appearance and functionality that was
different from the one forced from the superclass.
"""
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter.simpledialog import askstring
from tkinter.ttk import Frame, Label
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
        self.button_box()

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
        #tk.Toplevel.destroy(self)

    def body(self):
        """Creates the dialog's body."""
        self.box = Frame(self, height=0, width=300, borderwidth=2,
                         relief="groove")
        prompt_label = Label(self.box, text=" Please choose an action:",
                             font=("Segoe UI", 12, "bold"))
        prompt_label.grid(column=0, row=0, columnspan=2, sticky="nswe")
        self.bind("<Return>", self.finalize)
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
        new_file_button = tk.Button(self.box, text="Create new Project",
                                    command=self.new_file)
        copy_file_button = tk.Button(self.box, text="Copy Existing Project",
                                     command=self.copy_project)
        new_file_button.grid(column=0, row=1, sticky="nswe")
        copy_file_button.grid(column=1, row=1, sticky="nswe")

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
        """Handles the request of a filename for a new .inp file"""
        name_string = ""
        while name_string is not None:
            name_string = askstring(title="New Project",
                                    prompt=" Enter the new .inp filename:")
            if (name_string is not None and
                    name_string.lower().endswith(".inp")):
                if Path(self.new_file_dir, name_string).is_file():
                    showerror("Please provide another filename",
                              message=f"The filename {name_string} is already"
                                      + "taken in the selected directory.")
                else:
                    break
            elif (name_string is not None
                    and not name_string.lower().endswith(".inp")
                    and len(name_string) > 4):
                showerror("The new filename must end in .inp",
                          message="Please provide a filename that has .inp "
                                  "file extension")
        self.result = name_string
        self.finalize()

    def copy_project(self):
        """Handles the request of a .inp file from the native file dialog."""
        file_name = None
        while file_name is None:
            file_name = askopenfilename(filetypes=[("Input Files", ".inp")])
            if Path(self.new_file_dir, Path(file_name).name).is_file():
                showerror(title="Please choose another file",
                          message="A file of this name already exists in the "
                                  "target directory")
                file_name = None
            else:
                self.result = PurePath(file_name)
        if self.result is not None:
            self.finalize()


if __name__ == "__main__":
    root = tk.Tk()
    print(NewButtonDialog(root, new_file_dir=None).result)
