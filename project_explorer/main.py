#!/usr/bin/python3
"""
Specify the IMSIL Project Explorer as the main top level widget.

The application is a GUI that allows users to see an overview of all projects
and perform basic file operations with them. The main top level widget is a
Tkinter `Frame` that contains three further Frames in a grid layout that
contain the widgets of the application.

Author: Konstantinos Zafeiris 1183944
Date: March 2023

To run the application, simply execute the main.py using Python 3:

    $ python3 main.py

"""
import os
import platform
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import PurePath, Path
from tkinter import ttk, filedialog
from tkinter.ttk import Frame
from typing import Union, List

# Append working directory of IMSIL Parameter Editor to handle imports
parent_path = Path(__file__).parent.parent
sys.path.append(str(parent_path))
sys.path.append(str(parent_path.joinpath("input_file_generator_v3")))
from input_file_generator_v3 import main_window
from project_explorer.dialogs import NewButtonDialog
from project_explorer import project_browser as pb


class ProjectExplorer(Frame):
    """
    Represent the top-level main window of the Tkinter application.

    The ProjectExplorer class is responsible for creating and managing the
    main parent frame of the application. It contains the application's main
    overview where the imsil projects are shown. The class provides methods
    for the available buttons that handle user events and provide
    functionalities for the shown projects.
    """
    __slots__ = ("global_frame", "tree")

    def __init__(self, master=None) -> None:
        """
        Set up the GUI elements and create window on screen center.

        The window consists of a top frame called global_frame that sets
        3 sub-frames in a vertical grid and separators between them. The
        creation of the sub-frames elements are delegated to class methods.

        +----------------------------------------+
        |  self                                  |
        |  +----------------------------------+  |
        |  |            header_frame          |  |
        |  +----------------------------------+  |
        |  |            body_frame            |  |
        |  +----------------------------------+  |
        |  |            buttons_frame         |  |
        |  +----------------------------------+  |
        +----------------------------------------+
        """
        # Initialize Tk elements by using super's constructor
        super().__init__(master)
        # Create members
        self.parameter_editor = None
        self.master = master
        self.tree: Union[ttk.Treeview, None] = None
        self.opened_nodes: List[str] = []
        self.opened_nodes_fake: List[str] = []
        self.root_directory: Union[PurePath, None] = Path.home()
        self.root_node = None
        # self.logo_image: tk.PhotoImage = tk.PhotoImage(
        #    file="resources/logo1.png",
        #    width=400,
        #    name="photo_image")
        # Setup sub-frames
        header_frame = Frame(self, name="header_frame", height=200, width=200)
        body_frame = Frame(self, name="body_frame", height=200, width=200)
        buttons_frame = Frame(self, name="buttons_frame", height=200,
                              width=200)
        # Setup Header Frame
        self.setup_header_frame(header_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="we")
        # Header-Body frame separator
        # top_separator = ttk.Separator(self, orient="horizontal",
        #                              name="top_separator")
        # top_separator.grid(row=1, column=0, columnspan=2, sticky="we")
        # Setup Body Frame
        self.setup_body_frame(body_frame)
        body_frame.grid(row=3, column=0, columnspan=2, sticky="nswe")
        # Body-Buttons frame separator
        bottom_separator = ttk.Separator(self, orient="horizontal",
                                         name="bottom_separator")
        bottom_separator.grid(row=4, column=0, columnspan=2, sticky="swe")
        # Setup Buttons Frame
        self.setup_buttons_frame(buttons_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2)
        self.grid(column=0, row=0, sticky="snwe")
        self.columnconfigure("all", weight=1,
                             minsize=buttons_frame.winfo_reqwidth())
        self.rowconfigure(0, weight=0)
        self.rowconfigure([1, 2, 4], weight=0)
        self.rowconfigure(3, weight=10)
        self.rowconfigure(5, minsize=30, weight=0)
        # Set font for buttons
        buttons_font_style = ttk.Style()
        buttons_font_style.configure("ProjectExplorer.TButton",
                                     font=("Helvetica", 11))
        self.change_root(Path.home())
        self.update()

    # Gui Setup Methods
    def setup_header_frame(self, header_frame: Frame) -> None:
        """
        Set up the header frame.

        The header frame contains a logo image (not yet implemented),
        a path label, and a button for changing the path.

        Args:
            header_frame (Frame):
                The Tkinter Frame object representing the header frame in
                global_frame.
        """
        # image_label = ttk.Label(
        #   header_frame, width=450, name="image_label", image=self.logo_image)
        path_label = ttk.Label(
            header_frame, text="Root: ", name="path_label",
            wraplength=450, width=66, padding=(2, 0),
            anchor="w", background="#F2EFEF", relief="groove", justify="left",
            style="ProjectExplorer.TLabel")
        root_button = ttk.Button(
            header_frame, name="root_button", text="Change Root",
            width=12, style="ProjectExplorer.TButton",
            command=self.change_root)
        # image_label.grid(column=0, row=0, columnspan=2, sticky="nswe")
        path_label.grid(column=0, row=2, sticky="nswe")
        root_button.grid(column=0, row=2, sticky="nse")
        path_label.columnconfigure("all", weight=2,
                                   minsize=path_label.winfo_reqwidth())
        header_frame.columnconfigure("all", weight=1,
                                     minsize=header_frame.winfo_reqwidth())
        header_frame.rowconfigure("all", weight=1)

    def setup_body_frame(self, body_frame: Frame) -> None:
        """
        Set up the body frame.

         The body frame contains a Treeview widget and associated scrollbars.

        Args: body_frame (Frame):
            A Tkinter Frame object representing the
            main body of the application's main window.
        """
        buttons_font_style = ttk.Style()
        buttons_font_style.configure("Treeview", font=("Helvetica", 11))
        self.tree = ttk.Treeview(
            master=body_frame, style="Treeview", selectmode="browse",
            columns=("filename", "project", "date", "status", "filepath"),
            displaycolumns=["project", "date", "status"],
            yscrollcommand=lambda f, l: pb.autoscroll(
                vertical_scroll_bar, f, l))
        #  xscrollcommand=lambda f, l: pb.autoscroll(
        #     horizontal_scroll_bar, f, l))
        vertical_scroll_bar = ttk.Scrollbar(
            master=body_frame, orient="vertical", command=self.tree.yview)
        # Horizontal scroll bar is currently nonsensical to include since
        # resizing has been implemented
        # horizontal_scroll_bar = ttk.Scrollbar(
        #     master=body_frame, orient="horizontal", command=self.tree.xview)

        self.tree.heading("#0", text="Filename", anchor="w")
        self.tree.heading("project", text="Project Name", anchor="w")
        self.tree.heading("date", text="Modified", anchor="w")
        self.tree.heading("status", text="Status", anchor="w")
        self.tree.column("#0", stretch=True, width=350)
        # project column is hidden but used for the explorer view
        self.tree.column("project", stretch=False, width=0)
        self.tree.column("status", stretch=True, width=80)
        self.tree.column("date", stretch=True, width=80)
        self.tree["displaycolumns"] = ("status", "date")
        self.tree.bind("<<TreeviewOpen>>", pb.update_tree)
        self.tree.bind("<<TreeviewSelect>>", self.check_selection)
        self.tree.grid(column=0, row=0, sticky="nswe", columnspan=2)
        vertical_scroll_bar.grid(column=1, rowspan=1, row=0, sticky="nse")
        # horizontal_scroll_bar.grid(column=0, row=0, sticky="swe")
        body_frame.columnconfigure("all", weight=1)
        body_frame.rowconfigure("all", weight=1)

    def setup_buttons_frame(self, buttons_frame: Frame) -> None:
        """
        Set up the buttons frame.

        The buttons frame contains buttons and their specific style,
        and bind them to their respective methods.

        Args:
        buttons_frame (tk.Frame):
            The frame containing the buttons.
        """
        new_button = ttk.Button(
            buttons_frame, name="new_button", text="New",
            state="disabled", command=self.new_clicked,
            style="ProjectExplorer.TButton")
        edit_button = ttk.Button(
            buttons_frame, name="edit_button", text="Edit",
            state="disabled", command=self.edit_clicked,
            style="ProjectExplorer.TButton")
        view_button = ttk.Button(
            buttons_frame, name="view_button", text="View",
            state="disabled", command=self.view_clicked,
            style="ProjectExplorer.TButton")
        run_button = ttk.Button(
            buttons_frame, name="run_button", text="Run",
            state="disabled", command=self.run_clicked,
            style="ProjectExplorer.TButton")
        plot_button = ttk.Button(
            buttons_frame, name="plot_button", text="Plot",
            state="disabled", command=self.plot_clicked,
            style="ProjectExplorer.TButton")

        new_button.grid(column=0, row=2)
        edit_button.grid(column=1, row=2)
        view_button.grid(column=2, row=2)
        run_button.grid(column=3, row=2)
        plot_button.grid(column=4, row=2)
        buttons_frame.columnconfigure("all", weight=1)
        buttons_frame.rowconfigure("all", weight=1)

    # Bindings Methods
    def change_root(self, path_to_root=None) -> None:
        """
        Handle changing the root directory.

        Prompts the user to select a new directory through a file dialog and
        then updates the path label in the header frame with the new path.
        Finally, deletes all existing items from the tree view to prevent
        item duplication and re-populates it with the contents of the new
        directory. Additionally, enables the 'New' button in the buttons frame.

        Args:
            path_to_root (PurePath | str): Optional argument of a selected path
                if not None, the root will be this path, otherwise the user
                will be prompted to select one.
        """
        path_label = self.nametowidget("header_frame.path_label")
        if path_to_root is None:
            new_path = filedialog.askdirectory(mustexist=True,
                                               initialdir=self.root_directory)
            if new_path == () or None:
                return
            new_path = PurePath(new_path)
        else:
            new_path = path_to_root
        self.root_directory = Path(new_path)
        path_label.configure(text="Root: " + str(new_path))
        self.tree.delete(*self.tree.get_children(""))
        self.root_node = pb.populate_roots(self.tree, new_path)
        new_button = self.nametowidget("buttons_frame.new_button")
        new_button.configure(state="enabled")

    def check_selection(self, event: tk.Event):
        """
        Enable buttons depending on ttk.Treeview selection.

        Currently only the selection of an .inp file triggers enabling of
        the View and Edit buttons.

        Args:
            event (tk.Event):
                The event that triggers the method, usually a button click
                release event.
        """
        filepath = self.tree.set(event.widget.selection(), "filename")
        if filepath.endswith(".inp") or os.path.basename(filepath) == "INP":
            edit_button = self.nametowidget("buttons_frame.edit_button")
            edit_button.configure(state="enabled")
            view_button = self.nametowidget("buttons_frame.view_button")
            view_button.configure(state="enabled")
            return True
        else:
            buttons = self.nametowidget("buttons_frame").winfo_children()
            for button in buttons:
                if "new_button" not in str(button):
                    button.configure(state="disabled")
            return False

    def plot_clicked(self, event):
        """
        # TODO: After the plotting functionality is included assign the
        # TODO: plotting task to this function's calls.

        Args: event: The tk.event that called this method.

        Returns:

        """
        pass

    def view_clicked(self) -> None:
        """
        Open the file in the native file editor.

        Platform dependent behavior. Linux uses xdg-open which is available
        on most distros, in windows it opens the file with the application
        that the file extension is associated with. If none is, then the user
        will be asked to define one.
        """
        filepath = self.tree.set(self.tree.selection()[0], "filepath")
        if platform.system() == "Windows":
            os.startfile(filepath)
        else:
            subprocess.call(("xdg-open", filepath))

    def edit_clicked(self) -> None:
        """
        Open the Parameter Editor and load the current treeview selection.

        Since the input_file_generator_v3 uses relative imports, the working
        directory has to be changed so that all required classes are imported
        correctly, when finished, the working directory is set back to normal.
        """
        filepath = Path(self.tree.set(self.tree.selection()[0],
                                      "filepath"))
        # Check if selection is valid (either .inp or INP file)
        filename = os.path.basename(filepath)
        if not (filename.endswith(".inp") or filename == "INP"):
            return
        
        # If started from outside the directory, change cwd to where main.py is
        os.chdir(Path(os.path.abspath(__file__)).parent)
        # Because the parameter editor does not use relative inputs the
        # working directory has to be temporally changed to the directory of
        # the parameter editor so that everything is imported correctly
        os.chdir(PurePath("..//input_file_generator_v3"))
        self.parameter_editor = main_window.MainWindow(
            self, loaded_file_path=filepath)
        # While the parameter editor is opened the ProjectExplorer is waiting
        # for it to be closed before any further action is allowed and the
        # working directory is restored to the previous one
        os.chdir(PurePath("..//project_explorer"))

    def run_clicked(self):
        """

        # TODO: implement run button functionality
        Returns:

        """
        pass

    def new_clicked(self) -> None:
        """
        Open a two-button dialog and let user choose the desired action.

        The action always is the creation of a new file either on the
        directory that is selected, or on the root if none is. The file is
        either a copy of another file, or a new empty .inp file.
        """
        # can be either a str with a filename or a PurePath object
        if not self.tree.selection():
            new_file_dir = self.root_directory
        else:
            new_file_dir = Path(
                self.tree.set(self.tree.selection()[0], "filepath"))
            # if not new_file_dir.is_dir():
            #     new_file_dir = new_file_dir.parent
        # Result will be a str with the new filename or a PurePath of the
        # file to be copied
        new_button_result = NewButtonDialog(self, new_file_dir).result
        if isinstance(new_button_result, tuple):
            # Create new file new_button_result is tuple of (filename, dir)
            new_file_dir = Path(new_button_result[1])
            new_button_result = new_button_result[0]
            # Create empty file, new_button_result is path filename of new file
            if (not new_file_dir.is_dir() and str(new_file_dir)
                    != self.tree.set(self.root_node, 'filepath')):
                new_file_dir = new_file_dir.parent
            new_file_path = PurePath(new_file_dir, new_button_result)
            with open(new_file_path, "w", encoding="UTF-8") as f:
                f.write("")
            if self.tree.selection() == ():
                self.tree.selection_set("")
            pb.add_node(self.tree, new_file_dir, self.root_node,
                        Path(new_button_result).stem)

        elif issubclass(type(new_button_result), PurePath):
            # Copy file
            # new_button_result is complete PurePath of file to be created
            # new_file_dir is the filepath of the file to be copied
            shutil.copy2(new_file_dir, new_button_result)
            pb.add_node(self.tree, new_button_result.parent, self.root_node,
                        new_button_result.stem)
            if self.tree.selection() == ():
                self.tree.selection_set("")
        else:
            pass  # No action was chosen by the user


def make_flexible(obj, row=0, column=0, row_weight=1, column_weight=1):
    """
    Allow the top-level window to be flexible when using .grid().

    This is mandatory for the window resizing.
    Args:
        obj (tk.Tk): the root of the application
        row (int) : (Optional) the row to make flexible
        column (int) : (Optional) the column to make flexible
        row_weight (int) : (Optional) the weight of the row resizing
        column_weight (int) : (Optional) the weight of the column resizing
    """
    if row is not None:
        obj.rowconfigure(row, weight=row_weight)
    if column is not None:
        obj.columnconfigure(column, weight=column_weight)


def on_closing():
    """Handle window behavior on application closing"""
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        for item in app.tree.get_children():
            app.tree.delete(item)
        root.destroy()


if __name__ == "__main__":
    # Create the application loop and attach the Project Explorer to it
    root = tk.Tk()
    root.title("IMSIL Project Explorer")
    root.resizable(width=True, height=True)
    root.rowconfigure("all", weight=1)
    root.columnconfigure("all", weight=1)
    root.config(background="LightBlue4")
    root.protocol("WM_DELETE_WINDOW", on_closing)
    make_flexible(root)
    app = ProjectExplorer(root)
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    app.mainloop()
