"""Main entry point for the project. 

Parse parameters from the .tex files in the filenames list and store them in an
SQLite database as reStructuredText.

The name of the database (db_name) and the path to the manual (manual_path) are 
specified in this module.
"""

import os
import sqlite3
from code.parsing import parse_file
from code.database import create_tables, write_parameters

# Path to the .tex files of the manual
manual_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                           'manual'))

# Path to the database
#db_name = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',
#                                       'output1', 'parameters_new.db'))
db_name = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                       'parameters.db'))

# List of the files containing parameters 
filenames = ['rec_setup.tex', 'rec_atoms.tex', 'rec_ions.tex',
             'rec_material.tex', 'rec_snpar.tex', 'rec_separ.tex',
             'rec_damage.tex', 'rec_geometry.tex', 'rec_output.tex',
             'rec_crystal.tex']

# Parse private sections
parse_private = False

# The table names for the database are set according to the filenames without
# the extension
tablenames = [filename.removesuffix('.tex').removeprefix('rec_')
              for filename in filenames]


def get_full_manual_paths(filenames):
    """Return list of filenames with full path added.

    :param filenames: List of filenames of the .tex files containing the
    parameters
    :return: List of absolute .tex file paths
    """
    filenames_abs = []
    for filename in filenames:
        filenames_abs.append(os.path.abspath(os.path.join(manual_path,
                                                          filename)))
    return filenames_abs


if __name__ == '__main__':

    print('Set up:\n')
    print('Database stored in: ' + db_name + '\n')
    print('From manual stored in: ' + manual_path + '\n')
    print('Collecting from the following records: ')
    print(tablenames)
    print()
    print('Parsing private: ' + str(parse_private) + '\n')

    filenames = get_full_manual_paths(filenames)
    
    # Parse parameters
    parameters = []
    for filename, tablename in zip(filenames, tablenames):
        parameters.extend(parse_file(filename, tablename, parse_private))

    # Create and write into database
    if os.path.exists(db_name):
        os.remove(db_name)
    print(db_name)
    conn = sqlite3.connect(db_name)
    create_tables(conn, tablenames)
    write_parameters(conn, parameters)
    conn.close()

    print('Done.')
