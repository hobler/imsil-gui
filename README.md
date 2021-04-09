# The Program: 
`IMSIL-GUI` is a GUI for the binary collision simulator `IMSIL`, written in
python with Tkinter.

# Versions: 
The files in the directory `input_file_generator` represent the first version
of the GUI containing the code for the Boolean and Entry areas as well as
initial code to implement the index variable arrays (Author: Filip Humaj).

The files in the directory `input_file_generator_v2` represent the state of 
the GUI with the index variable arrays implemented. Furthermore, the code is 
cleaned up and restructured (Author: Christian Alacs).

The files in the directory `input_file_generator_v3` represent the current
state of the project.

# IMSIL input file generator
The main program file of the IMSIL input file generator is `main.py` 
(https://github.com/hobler/imsil-gui/blob/master/input_file_generator_v3/main.py). 
This program defines two windows: The Welcome Window and the
IMSIL Input Parameter Editor. 

## Welcome window
The Welcome Window serves the purpose to preconfigure the IMSIL Input
Parameter Editor by setting the simulation type and the number of regions
and atoms. Optionally, an existing input file may be loaded (currently
untested).   
 
To proceed to the IMSIL Input Parameter Editor, the user must press the `Open
IMSIL Input Parameter Editor` Button. This Button is only enabled if both
the `Number of Regions` and `Number of Atoms` values are greater than 0. 
In order to activate the Button, the fields have to lose focus (click in first 
field and fill in first value; click in second field, fill in second value and 
click out of field). In case the Button is enabled and the user enters invalid 
values before pressing the Button, a warning will be displayed, and the Button 
will be disabled again.  

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

# Files
In the following section (almost) all files of the project are briefly
described  

#### `input_file_generator_v3`:
-	`parameters.db`: the SQLite database
-	`main.py`: the top-level program file, containing the classes 
    `WelcomeWindow` and `ImsilInputParameterEditor`

#### `input_file_generator_v3\pics`:
-	`add.gif`, `minus.gif`: the pictures used for the +/- Buttons to 
     add/delete rows from the `POINT` index variable array 
-	`arrow.png`, `arrow_r.gif`, `arrow_l.gif`, `arrow_d.gif`, `arrow_u.gif`: 
    the pictures used for the arrow Buttons to expand/collapse the index
    variable array to the right/left/down/up  
-	`info_sign.gif`, `info_sign_1.gif`: the pictures used for the info Button 
    (`info_sign_1.gif` is currently used)

#### `input_file_generator_v3\data_model`:
-   `read_sqlite.py`, `data_list.py`, `input_file.py`: Classes used to manage
    the data or access the database

#### `input_file_generator_v3\UI\canvas`:
-   `blanc_canvas.py`: this class implements the canvas used for the scrolling 
    area in `ScrollFrame`

#### `input_file_generator_v3\UI\frames`:
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

#### `input_file_generator_v3\UI\widgets`:
-	`ShowAdvParButton.py`: this class was used to separate and toggle basic 
     and advanced parameters in the UI. This functionality is not in use in 
     the current version of the program.

# Functionality
The functionality of the program is briefly explained as follows:
 
The program can be started by running the file main.py. By doing so, the
Welcome Window will appear. In this window, the `Number of Regions` and
`Number of Atoms` values must be set to valid values (>0). Additionally, the
type of simulation can be set, and an input file can be loaded. If 
the values are set, the user can press the `Open IMSIL Input Parameter
Editor` Button.     

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


