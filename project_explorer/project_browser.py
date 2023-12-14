"""
Provide functions for creating and updating a Treeview widget.

Use tkinter, comply with Google Python style guide and PEP-8 naming conventions.

Functions:

    populate_tree(tree: ttk.Treeview, node: str, path: PurePath) -> None
        Create one level of tree below node.
    populate_roots(tree: ttk.Treeview, path: PurePath) -> str
        Assign root of tree to path and populate it
    update_tree(event) -> None
        Populate a node with its children when selected
    change_dir(tree: ttk.Treeview, path: PurePath) -> None
        # TODO: Is there any reason to keep this for now ???
    autoscroll(scrollbar, first, last) -> None

"""
import _tkinter
import itertools
import os
import random
import tkinter.ttk
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


def populate_tree(tree: ttk.Treeview, node: str, path: PurePath) -> None:
    """
    Create one level of tree below node.

    This function is called to populate one level of depth of the tree,
    and will be subsequently called whenever a new directory is opened.

    Note that the tree.set() method of ttk.TreeView is used for both
    setting and fetching an item.

    Args:
        tree:
            The tree
        node:
            Node id
        path:
            Path associated with the node.
    """
    # Fake project directories have their contents created when their parent
    # is accessed, therefore no further action is needed
    if node.startswith("TempDir"):
        return
    tree.delete(*tree.get_children(node))

    # Search for .inp files inside the passed directory
    inp_items = [item for item in os.listdir(path) if item.endswith(".inp")]
    inp_items.sort()
    # Create fake directory and assign it the project name for each .inp
    for inp_item in inp_items:
        project_name = os.path.splitext(inp_item)[0]
        if tree.set(node, "project") != project_name:
            fake_directory_id = tree.insert(
                node, "end", "TempDir" + str(next(TEMP_DIR_ID_COUNTER)),
                text=project_name)
            tree.set(fake_directory_id, "project", str(project_name))
            tree.set(fake_directory_id, "filepath", PurePath(path, inp_item))
    # Iterate through all items and assign them to node
    for item in sorted(os.listdir(path)):
        item_path = PurePath(path, str(item))
        item_type = "directory" if os.path.isdir(item_path) else "file"
        # Sort out items that should not be included in the tree
        if item_type == "directory":
            # Don't add directories that don't contain .inp files
            if not list(Path(item_path).rglob("*.inp")):
                continue
        elif item_type == "file":
            # Don't add files without qualified extension
            if not item.lower().endswith(ACCEPTED_FILE_EXTENSIONS):
                continue

        if item_type == "directory":
            item_id = tree.insert(node, "end", text=item, values=[item])
            tree.insert(item_id, 0, text=str(item))
            tree.set(item_id, "filepath", item_path)
        elif item_type == "file":
            item_id = tree.insert(node, "end", text=item, values=[item])
            tree.set(item_id, "date", get_date(os.stat(item_path).st_mtime))
            tree.set(item_id, "filepath", item_path)
            tree.set(item_id, "project", Path(item).stem)
            tree.set(item_id, "status", random.choice(
                ["Completed", "Running"]))  # Add status logic here
    # Iterate through all created children and move project specific files
    # to their respective fake project directory
    projects = [Path(inp_item).stem for inp_item in inp_items]
    for child in tree.get_children(node):
        child_name = tree.set(child, "filename")
        project = Path(child_name).stem     # project the file belongs to
        if project in projects:
            for other_child in tree.get_children(node):
                if (other_child.startswith("TempDir")
                        and tree.set(other_child, "project") == project
                        and other_child != child):
                    if Path(child_name).suffix == ".inp":
                        position = 0
                    elif Path(child_name).suffix == ".out":
                        position = 1
                    else:
                        position = "end"
                    tree.move(child, other_child, position)


def populate_roots(tree: ttk.Treeview, path: PurePath) -> str:
    """
    Assign root of tree to path and populate it.

    Args:
        tree:
            The tree
        path:
            Path of the root of the tree
    Return:
        str:
            Node id of root
    """
    node = tree.set("", "project", str(path))
    populate_tree(tree, node, path)
    return node


def update_tree(event: tkinter.Event) -> None:
    """Populate a node with its children when selected."""
    tree: ttk.Treeview = event.widget
    item = tree.selection()[0]
    node_path = PurePath(tree.set(item, "filepath"))
    populate_tree(tree, item, node_path)


def update_tree_by_node(tree, node) -> None:
    """Populate a node with its children when selected."""
    node_path = PurePath(tree.set(node, "filepath"))
    populate_tree(tree, node, node_path)


def add_node(tree: ttk.Treeview, new_file_path=None, root=None) -> None:
    """
    Add a new node to the tree while retaining the current view.

    Deletes all the to-be siblings of the new node and populates the
    parent with the new children including the new node. All open
    children and sub-children are saved based on their filename
    and then iterated over and re-opened.
    """
    item = None
    # If file has been copied to an unknown position, find the parent node
    if new_file_path is not None:
        for child in get_all_children(tree, root):
            if new_file_path == Path(tree.set(child, "filepath")).parent:
                item = child
                break
        if item is None:
            item = root
    else:
        item = tree.selection()[0]
    item = tree.parent(item)
    # If parent directory is fake, then update its parent
    if item.startswith("TempDir"):
        item = tree.parent(item)
    opened_nodes = []
    # Find all opened nodes below the parent
    for child in get_all_children(tree, item):
        if tree.item(child, 'open'):
            opened_nodes.append(tree.item(child, "text"))
    update_tree_by_node(tree, item)
    open_nodes(tree, item, opened_nodes)


def open_nodes(tree: ttk.Treeview, item: str, opened_nodes):
    """
    Iterate over the tree and open passed nodes

    Attempts to find all descendants of item and then
    open them if their text is found in the passed list.
    Due to the tree needing to update to populate newly
    opened nodes and then perhaps open their children
    the error raised from not finding a node is caught
    and the function is called recursively. The function
    runs n times, where n is the previously opened tree depth.
    """
    try:
        for child in get_all_children(tree, item):
            if tree.item(child, 'text') in opened_nodes:
                opened_nodes.remove(tree.item(child, 'text'))
                update_tree_by_node(tree, child)
                tree.item(child, open=True)
    except _tkinter.TclError:
        open_nodes(tree, item, opened_nodes)


def get_all_children(tree: ttk.Treeview, node):
    """Return all descendants of a node"""
    children = []
    children.extend(tree.get_children(node))
    for child in tree.get_children(node):
        children.extend(get_all_children(tree, child))
    return children


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


def get_date(os_date_stat):
    """
    Return the string that is assigned to the date column of the tree.

    If the date is today then return the time of creation, else return
    the complete date
    Args:
        os_date_stat:
            'os.stat' of the file
    Return:
        str:
            date string representation in human-readable form
    """
    datetimestamp = datetime.fromtimestamp(os_date_stat)
    if datetimestamp.day == datetime.now().day:
        return datetimestamp.strftime("%H:%M")
    else:
        return datetimestamp.date()
