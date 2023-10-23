"""
This module provides functions for creating and updating a Treeview widget
in tkinter, using the Google Python style guide and PEP-8 naming conventions.

Functions:

    populate_tree(tree: ttk.Treeview, node, path: PurePath) -> None
    populate_roots(tree: ttk.Treeview, path: PurePath) -> str
    update_tree(event) -> None
    change_dir(tree: ttk.Treeview, path: PurePath) -> None
    autoscroll(scrollbar, first, last) -> None

"""
import itertools
import os
import random
from datetime import datetime
from pathlib import PurePath, Path
from tkinter import ttk

ACCEPTED_FILE_EXTENSIONS = (".inp", ".out", ".his", ".cell", ".hisee",
                            ".hisne", ".hism", ".hisp", ".hisd", ".hisiv",
                            ".hisb", ".hiseb", ".hisab", ".hisaab", ".hist",
                            ".hiset", ".hisat", ".hisaat", ".rbs", ".his2",
                            ".hisee2", ".hisne2", ".his2b", ".hisa2b",
                            ".his2t", ".hisa2t", ".his3", ".hisee3", ".hisne3",
                            ".bck", ".pdv", ".pdi", ".pmax", ".pok", ".se",
                            ".tra")

TEMP_DIR_ID_COUNTER = itertools.count()


def populate_tree(tree: ttk.Treeview, node, path: PurePath):
    """
    Create the tree by searching the given directory using glob.

    This function is called to populate only one level of depth of the tree,
    and will be subsequently called whenever a new directory
    is opened.

    Note that the tree.set() method of ttk.TreeView is used for both
    setting and fetching an item.
    """
    # Fake project directories have their contents created when their parent
    # is accessed therefore no further action is needed
    if node.startswith("TempDir"):
        return
    tree.delete(*tree.get_children(node))

    # Search for .inp files inside the passed directory
    inp_items = [item for item in os.listdir(path) if item.endswith(".inp")]
    # Create fake directory and assign it the project name for each .inp
    for inp_item in inp_items:
        project_name = inp_item.replace(".inp", "")
        if tree.set(node, "project") != project_name:
            fake_directory_id = tree.insert(node, "end",
                                            "TempDir" + str(
                                                next(TEMP_DIR_ID_COUNTER)),
                                            text=project_name)
            tree.set(fake_directory_id, "project", str(project_name))
            tree.set(fake_directory_id, "filepath", PurePath(path, inp_item))
    # Iterate through all items and assign them to the passed node
    for item in os.listdir(path):
        item_path: PurePath = PurePath(path, str(item))
        item_type = "directory" if os.path.isdir(item_path) else "file"
        if item_type == "directory":
            # Don't add directory to the tree if it doesn't contain an .inp
            if sum(1 for _ in Path(item_path).rglob("*.inp")) == 0:
                continue
        elif item_type == "file":
            # Don't show irrelevant files
            if not item.lower().endswith(ACCEPTED_FILE_EXTENSIONS):
                continue

        if item_type == "directory":
            item_id = tree.insert(node, "end", text=str(item),
                                  values=[item])
            tree.insert(item_id, 0, text=str(item))
            tree.set(item_id, "filepath", item_path)
        elif item_type == "file":
            item_id = tree.insert(node, "end", text=str(item),
                                  values=[item])
            tree.set(item_id, "date", datetime.fromtimestamp(
                os.stat(item_path).st_mtime).date())
            tree.set(item_id, "filepath", item_path)
            tree.set(item_id, "project", Path(item).stem)
            tree.set(item_id, "status", random.choice(
                ["Completed", "Running"]))  # Add status logic here
    # Iterate through all created children and move project specific files
    # to their respective fake project directory
    for child in tree.get_children(node):
        child_name = tree.set(child, "filename")
        project = Path(child_name).stem
        if project in [Path(x).stem for x in inp_items]:
            for other_child in tree.get_children(node):
                if (other_child.startswith("TempDir")
                        and tree.set(other_child, "project") == project
                        and other_child != child):
                    position = "end"
                    if Path(child_name).suffix == ".inp":
                        position = 0
                    elif Path(child_name).suffix == ".out":
                        position = 1
                    tree.move(child, other_child, position)


def populate_roots(tree: ttk.Treeview, path: PurePath) -> str:
    """Assigns the selected root as the root of the whole tree and
    populates it with its children files or directories.
    """
    node = tree.insert("", "end", text=str(path),
                       values=["", "", "", "", path])
    populate_tree(tree, node, path)
    return node


def update_tree(event):
    """When an existing node is opened, populates the opened node with its
    children.
    """
    tree: ttk.Treeview = event.widget
    item = tree.selection()[0]
    node_path: PurePath = PurePath(tree.set(item, "filepath"))
    populate_tree(tree, tree.focus(), node_path)


def change_dir(tree: ttk.Treeview, path: PurePath):
    """Handle changing the base root of the TreeView

    When a changing root is requested all existing children of the root node
    are deleted a new node is selected as root and is then populated by its
    children.

    Deprecated, to be deleted.
    """
    if tree.parent(str(path)):
        path = os.path.abspath(tree.set(str(path), "filename"))
        if os.path.isdir(path):
            os.chdir(path)
            tree.delete(tree.get_children("")[0])
            populate_roots(tree, path)


def autoscroll(scrollbar, first, last):
    """Hide and show scrollbar as needed for navigation in the treeview."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        scrollbar.grid_remove()
    else:
        scrollbar.grid()
    scrollbar.set(first, last)
