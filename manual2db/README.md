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

In the main file **manual2db.py** set the following variables:

```db_name:``` filename for the database

```manual_path:``` path were the .tex files are stored

```filenames:``` list of the files containing parameters

```parse_private:``` boolean value if private sections should be included or not

#### Example:
```python
db_name = 'parameters.db'
manual_path = 'C:\\Users\\myname\\somedirectory\\manual'
filenames = ['setup.tex', 'atoms.tex', 'ions.tex', 'material.tex', 'snpar.tex', 
             'separ.tex', 'damage.tex', 'geom.tex', 'output.tex', 'xtal.tex']
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

