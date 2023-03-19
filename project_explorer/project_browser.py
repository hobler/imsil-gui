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
import os
import random
from datetime import datetime
import pathlib
from pathlib import PurePath
from tkinter import ttk

ACCEPTED_FILE_EXTENSIONS = (".inp", ".out", ".his", ".cell", ".hisee",
                            ".hisne", ".hism", ".hisp", ".hisd", ".hisiv",
                            ".hisb", ".hiseb", ".hisab", ".hisaab", ".hist",
                            ".hiset", ".hisat", ".hisaat", ".rbs", ".his2",
                            ".hisee2", ".hisne2", ".his2b", ".hisa2b",
                            ".his2t", ".hisa2t", ".his3", ".hisee3", ".hisne3",
                            ".bck", ".pdv", ".pdi", ".pmax", ".pok", ".se",
                            ".tra")


def populate_tree(tree: ttk.Treeview, node, path: PurePath):
    """Create the tree by searching the given directory using glob."""
    tree.delete(*tree.get_children(node))
    for item in os.listdir(path):  # Iterate through children of passed node
        item_path: PurePath = PurePath(path, str(item))
        item_type = "directory" if os.path.isdir(item_path) else "file"
        if item_type == "directory":
            # Don't add directory to the tree if it doesn't contain an .inp
            if sum(1 for _ in pathlib.Path(item_path).rglob("*.inp")) == 0:
                continue
        elif item_type == "file":
            # Don't show irrelevant files
            if not item.lower().endswith(ACCEPTED_FILE_EXTENSIONS):
                continue

        if item_type == "directory":
            item_id = tree.insert(node, "end", text=str(item), values=[item])
            tree.insert(item_id, 0, text=str(item))
            for child in os.listdir(item_path):
                if child.lower().endswith(".inp"):
                    tree.set(item_id, "project", child.replace(".inp", ""))
            tree.set(item_id, "filepath", item_path)
        elif item_type == "file":
            item_id = tree.insert(node, "end", text=str(item), values=[item])
            if item_path.suffix == ".inp":
                parent_id = tree.parent(item_id)
                if tree.set(parent_id, "project") == "":
                    tree.set(item_id, "project", item.replace(".inp", ""))
            tree.set(item_id, "date", datetime.fromtimestamp(
                os.stat(item_path).st_mtime).date())
            tree.set(item_id, "status", random.choice(
                ["Completed", "Running"]))
            tree.set(item_id, "filepath", item_path)


def populate_roots(tree: ttk.Treeview, path: PurePath) -> str:
    """Assigns the selected root as the root of the whole tree and
    populates it with its children files or directories.
    """
    node = tree.insert("", "end", text=str(path),
                       values=[path, "", "", "", path])
    for child in os.listdir(path):
        if child.lower().endswith(".inp"):
            tree.set(node, "project", child.replace(".inp", ""))
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
