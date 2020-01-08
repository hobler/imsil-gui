# IMSIL GUI

GUI for the binary collision simulator IMSIL written in python with TKinter.

## IMSIL input file generator

The main program file of the IMSIL input file generator is [main.py](https://github.com/hobler/imsil-gui/blob/master/input_file_generator/main.py). 

This program defines two windows: First there is a welcome window where the user can preconfigure the second window which is the IMSIL input parameter editor.

### Welcome window

The first configuration option in the welcome window is the type of the simulation. The type of simulation is used to group the most common parameters for this type of simulation at the top of the window.

The second configuration option provides the ability to load an existing IMSIL input file. The data of the database will be updated with the data in the input file (currently non-functional).
  
With a button at the bottom of the welcome window, the IMSIL input parameter editor can be opened.

### IMSIL input parameter editor window

The IMSIL input parameter editor window contains a notebook with tabs. The names of the tabs are the same as the names of the tables from the database, which are the same as the names of the IMSIL input file records. Currently the database is represented by the [parameters.db](https://github.com/hobler/imsil-gui/blob/master/input_file_generator/parameters.db) file. The sqlite_master table, which is generated automatically by sqlite, is used to get all table names that are in the database. This work is done by the class [SqliteMaster.py](https://github.com/hobler/imsil-gui/blob/master/input_file_generator/DataModel/Table/SqliteMaster.py). For each table name a new page in the notebook is created. On every new page there is always only one Frame. This Frame is represented by the class [DbFrame](https://github.com/hobler/imsil-gui/blob/master/input_file_generator/UI/Frames/db_frame.py). This Frame uses the class [DatabaseTable](https://github.com/hobler/imsil-gui/blob/master/input_file_generator/DataModel/Table/DatabaseTable.py) which reads the table from the database and saves it to a list of tuples. Each tuple is a table row. The logic behind each tab where you can scroll through all parameters, add/delete parameters and let you show a detailed information about the parameter is in the class [ImsilScrollFrame](https://github.com/hobler/imsil-gui/blob/master/input_file_generator/UI/Frames/scroll/imsil_scroll_frame.py). The class [DataList](https://github.com/hobler/imsil-gui/blob/master/input_file_generator/DataModel/DataList.py) is used for all parameters from each table in the GUI to save the parameter name, the corresponding widget and the variable that hold the value of the widget. As there are parameters which are bind to index variables, this class has to be extended with the ability to set/get not only the widget of a parameter but also the widgets and variables of the index variables of the parameter.
