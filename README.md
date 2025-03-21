# The Program: 
`IMSIL-GUI` is a GUI for the binary collision simulator `IMSIL`, written in
python with Tkinter.

## Versions: 
The files in the directory `input_file_generator` represent the first version
of the GUI containing the code for the Boolean and Entry areas as well as
initial code to implement the index variable arrays (Author: Filip Humaj).

The files in the directory `input_file_generator_v2` represent the state of 
the GUI with the index variable arrays implemented. Furthermore, the code is 
cleaned up and restructured (Author: Christian Alacs).

The files in the directory `input_file_generator_v3` represent the current
state of the project (Author: Florian Asperger).

The files in the directory `project_explorer` provide a GUI for managing and
viewing projects in a directory (Author: Konstantinos Zafeiris)

## How to start `IMSIL-GUI`
### Used libraries
The following libraries need to be installed in order to run the application.
-	`Pmw`: used to create tooltips

In addition, the `f90nml`package is used to load and save IMSIL input files. 
To avoid installation problems, the source code   **(Version &ge; 1.4.4)** has
been added to the project.

### Running the program

#### Running the program from the `project explorer` directory
To launch the project explorer GUI and access the IMSIL Input File generator
within it, navigate to the `imsil-gui/project_explorer` directory and execute
the main script by entering:

```
$ python3 main.py
```

Once the GUI is open, you can run the IMSIL Input File generator directly 
from the Project Explorer GUI. Simply select a project file and click on the 
`Edit` button to begin.

#### Running the IMSIL Input FIle generator as a standalone program
The main script of the IMSIL input file generator is `main.py` 
(https://github.com/hobler/imsil-gui/blob/master/input_file_generator_v3/main.py). 
The only functionality of the `main.py` script is to generate the Welcome 
window, which in turn allows to open the IMSIL Input Parameter Editor. Start
`IMSIL-GUI` by passing the main script to a Python 3 interpreter:

    $ python3 main.py

## IMSIL Input File Generator Main Window
The Main Window serves the purpose create a new or load an existing input 
file for IMSIL. 

To **create a new input file**, click on the "New Input File..." button. This will 
open a file dialog which asks you for a name and directory for the new file.
After that, the parameters will be initialized with the default values.

For **loading an existing input file**, click on the "Load Existing Input File..." 
button, which opens a file dialog to select the file.
After that, the parameters will be loaded from the existing file.

The currently selected file will be visible on the bottom of the window.

Ions and Regions can be edited directly in the Main Window. Additional regions 
can be inserted by using the "+" buttons next to the regions. Remove regions by 
clicking the "-" button next to them. Region positions can be swapped by the
arrow buttons. To change the name of the Ions or Regions, click on the entry
box containing either a previous name or "< click to change >". Editing will
directly change the parameters NR and NATOM as well as Ions and Regions 
parameters.

Additionally, the Ion energy and the Regions geometry can be edited in this window.

To edit other parameters, the user has to open the Parameter Editor by clicking 
on the "Parameter Editor..." button.

## IMSIL Input Parameter Editor window
The IMSIL Input Parameter Editor window contains a notebook with tabs. The
names of the tabs are the same as the names of the tables from the database. 
These are the same as the names of the IMSIL input file records. Currently, 
the database is represented by the `parameters.db` file. The sqlite_master
table, which is generated automatically by sqlite, is used to get all table
names that are in the database. This work is done by the function
`get_database_table_names` of the `read_sqlite` module.      
 
For each table name a new page (tab) in the notebook is created. On every new
page there is a TabFrame (class `TabFrame`). This frame uses the class
`DatabaseTable`, which reads the table from the database and saves it to a
list of `DatabaseTableRow`s.    

The logic behind each tab where you can scroll through all parameters is in
the class `ScrollFrame`. `ScrollFrame` creates `BlancFrames` for the Boolean
and Entry type parameters and an `IndexVariableArrayFrame` for every index
variable array. The class `DataList` is used for all parameters from each
table in the GUI to save the parameter name, the corresponding widget and
the variable that holds the value of the widget. As there are parameters
which are bound to index variables, this class has to be extended with
the ability to set/get not only the widget of a parameter but also the
widgets and variables of the index variables of the parameter.

When closing the Parameter Editor, a message box will appear, asking the user to
confirm or cancel the changes.

# Files
In the following section (almost) all files of the project are briefly
described.

#### `project_explorer:`
- `main.py`: Launches the main window application and handles the event loop
    and all user interactions
- `dialogs.py`: Handles the creation, actions and deletion of dialogs that are
  used by the main application window for user input.
- `project_explorer.py`: Defines methods for populating, displaying and 
  handling changes in the TreeView widget of the main application

#### `input_file_generator_v3`:
-	`parameters.db`: the SQLite database
-	`main.py`: contains the main function, which opens the Welcome Window
-	`welcome_window.py`: The `WelcomeWindow` class (obsolete)
-	`main_window.py`: The MainWindow class. replacing the WelcomeWindow
-	`parameter_editor_window.py`: contains the `ImsilInputParameterEditor` class.
-	`edit_window.py`: contains the `EditWindow` and `RegionFrame` classes.
-	`utility.py`: contains the `center_window` function

#### `input_file_generator_v3/pics`:
-	`add.gif`, `minus.gif`: the pictures used for the +/- Buttons to 
     add/delete rows from the `POINT` index variable array 
-	`arrow.png`, `arrow_r.gif`, `arrow_l.gif`, `arrow_d.gif`, `arrow_u.gif`: 
    the pictures used for the arrow Buttons to expand/collapse the index
    variable array to the right/left/down/up  
-	`info_sign.gif`, `info_sign_1.gif`: the pictures used for the info Button 
    (`info_sign_1.gif` is currently used)

#### `input_file_generator_v3/data_model`:
-   `read_sqlite.py`, `data_list.py`, `input_file.py`: Classes used to manage
    the data or access the database
-   `element.py`, `element.f90`: Classes and files to manage molecular formulas
-   `iv_data.py`: Classes `IVData` and `IVDict` to store the data from index 
    variable arrays and provide some helper functions.
-   `parameter_data.py`: ParameterData class. Stores parameters.

#### `input_file_generator_v3/UI/canvas`:
-   `blanc_canvas.py`: this class implements the canvas used for the scrolling 
    area in `ScrollFrame`

#### `input_file_generator_v3/UI/frames`:
-   `tab_frame.py`: this module implements the Frame used as a container for 
    the ScrollFrames in every tab of the notebook. This module also calls the
    methods to retrieve the data from the database, regroup it and add it to
    the ScrollFrames
-	`blanc_frame.py`: this class implements the Frame used as a base for all
    other Frames in the program. It contains functionality to control the 
    layout of each Frame by setting the weights of the rows and columns using 
    Frame IDs.  
-	`scroll_frame.py`: this class implements the scrolling area in every tab
    as well as the methods to add parameters to the corresponding content 
    Frames inside the scrolling area. This class also contains the methods to 
    add every type of element (Labels, Entries, etc.) to the Frames.  
-	`ivarray_frame.py`: this class implements every method regarding index 
    variable arrays. It contains methods to get their state, expand/collapse
    them, add/delete rows, track their values and set them accordingly as well
    as the general logic for their layout.
-	`target_frame.py`: Frame containing region edit frames. Used in the Main 
    Window to edit the regions.

#### `input_file_generator_v3/UI/widgets`:
-	`ShowAdvParButton.py`: this class was used to separate and toggle basic 
     and advanced parameters in the UI. This functionality is not in use in 
     the current version of the program.

# Functionality
The functionality of the Project Explorer GUI is as follows:
## Project Explorer Functionalities

The Project Explorer follows the same behavior as a common file browser, 
showing the directories, projects and project files in a TreeView manner.
By selecting a directory as the root of the tree via clicking the `Root` 
button the user has the following options by clicking their corresponding
buttons.

-  `New` Can be used to create a new project file or copy an existing
    one to a selected location.
- `Edit` Can be used when a project file is selected, opens the Imsil GUI
    parameter editor.
- `View` Opens the local editor to manually view and modify the project file.
- `Run` Not yet implemented
- `Plot` Not yet implemented

The functionality of the ISMIL Input Parameter is briefly explained as follows:
 
## Imsil Input Parameters
The program can be started by running the file main.py. By doing so, the
Main Window will appear. After creating or loading a file, the Ions and Regions 
can be edited. To edit other Parameters, the user can press the 
`Parameter Editor...` Button.

Next, a small window will appear, informing the user that the data is loading. 
Once the data has been fully loaded, and the notebook is set up, the small
window closes, and the IMSIL Input Parameter Editor appears. The Editor has
several tabs, each following the same logic and structure. Every tab can
consist of three sections: The Flags, the Entries and the index variable
arrays. Some tabs contain all three sections, some contain only one or
two of them. Regardless, their order is always the same. First the Flags
are displayed, followed by the Entries, followed by the index variable
arrays. Within each section the elements are ordered alphabetically.
 
The number of Flags and Entries per row can be set in the program using the
two variables `BOOL_PARAMS_PER_ROW` and `ENTRY_PARAMS_PER_ROW` in the
`scroll_frame.py` file. For index variable arrays only one array is
possible per row, thus there is no variable defining the number of index
variable arrays per row.

## Index Variable Arrays

The index variable arrays can be expanded and collapsed with the help of the
arrow Buttons on the right-hand side of the row. Depending on the dimension
of each index variable array, one or two arrow Buttons are available. The
logic of the index variable arrays is as follows: 
  
- If the array is fully collapsed (only one Entry is visible), the single Entry 
  can have three different states: it can be empty, it can hold a value, or it 
  can display the text “Multiple values”. The first two states are the same 
  (empty is a value), and they signify that every element of the index
  variable array has the same value as the single Entry. The third state
  signifies that the index variable array has at least two elements with 
  different values. If the value of the single Entry is modified, all
  elements of the index variable array will be set to this new value.       
- If the array is 1-dimensional, and it is expanded in this dimension, every
  Entry can be set separately. If the array gets collapsed afterwards, the
  single Entry will either show the value, set for all elements (if they are
  identical) or show “Multiple values” (if the elements are not identical).   
- If the array is 2-dimensional, and it is only expanded in one dimension, 
  the elements in the first row/column will work the same way as the single
  Entry in the collapsed state. This means they will show if all elements of
  the row/column have the same value or not. If their value is modified, all
  elements of the row/column are modified. Example: If the array is 
  2-dimensional and expanded only to the right, every Entry in the first row
  will either show a value or the text “Multiple values”. If an Entry shows
  a value, it means that every element of that column has the same value. If 
  it shows “Multiple values” at least two elements of that column have 
  different values. By setting any of these first elements, all elements of 
  that row/column will be set to the same value. Therefore, if only the 
  element in the first row/column should be set instead of all elements in 
  that column/row, the array needs to be fully expanded before entering the 
  value.              
- If the array is 2-dimensional, and it is expanded in both dimensions, every 
  Entry can be set separately. If the array gets collapsed in any dimension 
  afterwards, the first row/column (or the single Entry for the fully 
  collapsed state) will either show the value, set for all elements in
  that column/row (if they are identical) or show “Multiple values” (if the
  elements are not identical).     
- For the POS index variable array (whose index variable internally is called
  POINT), new rows can be added by pressing the ‘+’ Button. In the expanded 
  state, existing rows can be deleted by pressing the ‘-’ Button. However, 
  there is always at least one Entry (the first Entry cannot be deleted). The 
  logic for the values of the new rows is as follows:
  -	If the array is collapsed and the single Entry is set to a value, every
    new row added, by pressing the ‘+’ Button, will have the value of the 
    single Entry.  
  -	If the array is collapsed and the single Entry shows the text “Multiple 
    values”, every new row added, by pressing the ‘+’ Button, will have the
    value ‘’ (empty).  
  -	If the array is expanded, every row added, by pressing the ‘+’ Button, 
    will have the value ‘’ (empty). 



