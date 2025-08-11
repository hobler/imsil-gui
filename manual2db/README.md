# manual2db
Repository for PR 362.156 2019SS

The goal of this project was to collect the parameters for the IMSIL simulation 
program from the manual written in LaTeX, and to store them in an SQLite 
database in reStructuredText.

In order to check the parameters for validity, they can be displayed in the 
browser as part of the sphinx documentation

## Installation

The only 3rd party package used was **sqlite3** for generating, writing and 
reading databases. To install it:

```bash
pip install sqlite3
```


## Usage


### Setup global variables

In the file ```manual_version``` set the name of the folder which contains the 
manual .tex files, such as the parameter files. It is assumed that the file
folder is in the same folder as the ```manual2db.py``` file. The paramter files 
**must** have the prefix **param_**, otherwise the script will not find them.

In the main file **manual2db.py** set the following variables:

```db_name:``` filename for the database

```parse_private:``` boolean value if private sections should be included or not

#### Example:
```text
manual_version = manual_2024-03
```

```python
db_name = 'parameters.db'
parse_private = False
```

### Change LaTeX files

As discussed with my supervisor, two mistakes had to be corrected in the files 
before parsing them:

In **output.tex** there is a missing backslash in the description of the 
parameter TITLTA. Change **texttt{** to **\texttt{**

In **geom.tex** the default values of the parameters POINTS and POS were 
commented. Just remove the two '%' characters.


### Generate database

In order to actually parse the files and generate the database, run 
**manual2db.py** from the root directory of the project.

**NOTE: If there is already a database with the same name in the output folder,
the file is overwritten.


### Check parameters for validity

In order to check the parameters you can either open up the 
[DB Browser for SQLite](https://sqlitebrowser.org/) and go through the tables 
manually.

There is currently a column called **condition** in the parameter database,
whose contents are parsed from the **range** conditions when generating the
database. This column is to be used to automatically check the validity of
the parameters in the GUI, using _validate_ or a similar function. However, this
is not yet implemented.

