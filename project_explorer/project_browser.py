"""
Provide functions for creating and updating a Treeview widget.

Use tkinter, comply with Google Python style and PEP-8 naming conventions.

Functions:

    populate_tree(tree: ttk.Treeview, node: str, path: PurePath) -> None
        Create one level of tree below node.
    populate_roots(tree: ttk.Treeview, path: PurePath) -> str
        Assign root of tree to path and populate it
    update_tree(event) -> None
        Populate a node with its children when selected
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


def populate_tree(tree: ttk.Treeview, node: str, path) -> None:
    """
    Populate one level of the Treeview below `node`.
    Show .inp files directly as 'INP' without creating a folder.
    """
    tree.delete(*tree.get_children(node))

    path = Path(path)  # sicherstellen, dass es ein echtes Path-Objekt ist

    for item in sorted(os.listdir(path)):
        item_path = path / item
        is_dir = item_path.is_dir()
        is_inp = item_path.suffix.lower() == ".inp" or item_path.name == "INP"

        if is_dir:
            # Prüfe, ob Unterverzeichnisse .inp Dateien enthalten
            has_inp_files = any(
                f.is_file() and (f.suffix.lower() == ".inp" or f.name == "INP")
                for f in item_path.rglob("*")
            )
            if not has_inp_files:
                continue
            item_id = tree.insert(node, "end", text=item, values=[item])
            tree.set(item_id, "filepath", item_path)
            tree.insert(item_id, "end", text="")  # Dummy-Knoten
        elif item_path.is_file():
            if item_path.suffix.lower() in ACCEPTED_FILE_EXTENSIONS or is_inp:
                display_name = "INP" if is_inp else item
                item_id = tree.insert(node, "end", text=display_name, values=[item])
                tree.set(item_id, "filepath", item_path)
                tree.set(item_id, "date", get_date(os.stat(item_path).st_mtime))
                tree.set(item_id, "project", display_name)
                tree.set(item_id, "status", random.choice(["Completed", "Running"]))


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
    tree.set("", "filepath", str(path))
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
    """
    Populate a node with its children when selected.

    Args:
        tree (ttk.TreeView) : The tree to act upon.
        node (str) : The id of the node from which to start updating the tree.
    """
    node_path = PurePath(tree.set(node, "filepath"))
    populate_tree(tree, node, node_path)


def add_node(tree: ttk.Treeview, new_file_path=None, root=None, new_node=None):
    """
    Add a new node to the tree while retaining the current view.

    Deletes all the to-be siblings of the new node and populates the
    parent with the new children including the new node. All open
    children and sub-children are saved based on their filename
    and then iterated over and re-opened.

    Args:
        tree (ttk.TreeView) : The tree to act upon
        new_file_path (str) : The path to the item that the newly added node
            represents
        root (str) : The id of the root of the tree, required when the new node
            is added to a non-opened location of the tree
        new_node (str) : The id of the newly added node, required to open the
            new node when a node of the same name already exists and is opened
            on the tree
    """
    item = None
    # If file has been copied to an unknown position, find the parent node
    if new_file_path is not None:
        for child in get_all_children(tree, root):
            if new_file_path == Path(tree.set(
                                     child, "filepath")).parent:
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
    opened_nodes = [new_node]
    # Find all opened nodes below the parent
    for child in get_all_children(tree, item):
        if tree.item(child, 'open'):
            opened_nodes.append(tree.item(child, "text"))
    update_tree_by_node(tree, item)
    open_nodes(tree, item, opened_nodes)
    open_path_to_new_node(tree, root, new_file_path)


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

    Args:
        tree (ttk.TreeView) : The tree to act upon
        item (str) : The node from which to start updating the tree
        opened_nodes List[str] : List of the node texts that were opened and
            need to be opened after updating the tree
    """
    try:
        for child in get_all_children(tree, item):
            if tree.item(child, 'text') in opened_nodes:
                if tree.item(child, 'open') == 1:
                    continue
                opened_nodes.remove(tree.item(child, 'text'))
                update_tree_by_node(tree, child)
                tree.item(child, open=True)
    except _tkinter.TclError:
        open_nodes(tree, item, opened_nodes)


def open_path_to_new_node(tree: ttk.Treeview, root, new_node_path: Path):
    """
    Find all ancestor nodes of the new node and open them.

    Args:
        tree (ttk.TreeView) : The tree to act upon
        root (str) : The id of the tree root
        new_node_path (Path) : The Path on the filesystem of the new node
    """
    nodes = new_node_path.parts
    for node in nodes:
        for child in get_all_children(tree, root):
            if tree.item(child, 'text') == node:
                update_tree_by_node(tree, child)
                tree.item(child, open=True)
                break


def get_all_children(tree: ttk.Treeview, node):
    """
    Return all descendants of a node
    Args:
        tree (ttk.TreeView) : The tree to act upon
        node (str) : The id of the node from which to find all children
    """
    children = []
    children.extend(tree.get_children(node))
    for child in tree.get_children(node):
        children.extend(get_all_children(tree, child))
    return children


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
