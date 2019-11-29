# IMSIL GUI

GUI for the binary collision simulator IMSIL written in python with TKinter.

## IMSIL input file generator

The main program file of the IMSIL input file generator is [main.py](https://github.com/hobler/imsil-gui/blob/master/IMSIL%20Input%20File%20Generator/main.py). 

This main program contains two windows: First there is a welcome window where the user can preconfigure the second window which is the IMSIL input file generator.

### Welcome window

The first configuration in the welcome window is the type of the simulation. This type of simulation is used to set the right common parameters at the beginning of a list with parameters. 
The second configuration is the ability to load an existing IMSIL input file.
With a button on the end of the welcome window, the IMSIL input file generator can be finally opened.

### IMSIL input file generator window

The IMSIL input file generator window contains a notebook with tabs. The names of the tabs are the same as the names of the tables from the database. Currently the database is represented by the [parameters.db](https://github.com/hobler/imsil-gui/blob/master/IMSIL%20Input%20File%20Generator/parameters.db) file. The sqlite_master table, which will be generated automatically by sqlite, will be used to get all table names that are in the database. This work will be done by the class [SqliteMaster.py](https://github.com/hobler/imsil-gui/blob/master/IMSIL%20Input%20File%20Generator/DataModel/Table/SqliteMaster.py). 
For each table name a new page in the notebook will be created. On every new page there is always only one Frame. This Frame will be represented by the class [DbFrame](https://github.com/hobler/imsil-gui/blob/master/IMSIL%20Input%20File%20Generator/UI/Frames/db_frame.py). This Frame use the class [DatabaseTable](https://github.com/hobler/imsil-gui/blob/master/IMSIL%20Input%20File%20Generator/DataModel/Table/DatabaseTable.py) which reads the table from the database and save it to a list of tuples. Each tuple is a table row. 
The logic behind each tab where you can scroll through all parameters, add / delete parameters and let you show a detail information about the parameter is in the class [ImsilScrollFrame](https://github.com/hobler/imsil-gui/blob/master/IMSIL%20Input%20File%20Generator/UI/Frames/scroll/imsil_scroll_frame.py).
The class [DataList](https://github.com/hobler/imsil-gui/blob/master/IMSIL%20Input%20File%20Generator/DataModel/DataList.py) is used for all parameters from each table in the GUI to save the parameter name, the corresponding widget and the variable that hold the value of the widget. As there are parameters which are bind to index variables, this class has to be extended with the ability to set/get not only the widget of a parameter but also the widgets and variables of the index variables of the parameter.
