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
import re

##### Function definitions #####

def get_full_manual_paths(filenames, manual_path):
    """Return list of filenames with full path added.

    :param filenames: List of filenames of the .tex files containing the
    parameters
    :param manual_path: Path to the manual.tex file
    :return: List of absolute .tex file paths
    """
    filenames_abs = []
    # Other files should be in the same folder as the manual.tex file
    manual_path = os.path.dirname(manual_path)
    
    for filename in filenames:
        filenames_abs.append(os.path.abspath(os.path.join(manual_path,
                                                          filename)))
    return filenames_abs

def get_param_filenames(manual_path):
    """
    Return list of the filenames in the parameters section of the manual.
    
    :param manual_path: Path to the manual.tex file
    :return: List of filenames in the parameters section of the manual
    """
    
    with open(manual_path, 'r', encoding='utf-8') as manual:
            manual_content = manual.read()
        
    # Find all parameter filenames in the file by matching "param_*.tex"
    regex_filenames = re.findall(r'param_\w+\.tex', manual_content)
    
    return regex_filenames

##### Start of script #####

# Generate the filepath for the manual.tex file from manual file
with open('manual_version', 'r') as file:
    manual_subfolder = file.read().strip()
    manual_filename = manual_subfolder.split("_")[0] + '.tex'
    
current_file_location = os.path.dirname(__file__)
manual_path = os.path.join(current_file_location, 
                           manual_subfolder, 
                           manual_filename)

# Path to the database
#db_name = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',
#                                       'output1', 'parameters_new.db'))
db_name = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                       'parameters.db'))

# List of the files containing parameters 
filenames = get_param_filenames(manual_path)

# Parse private sections
parse_private = False

# The table names for the database are set according to the filenames without
# the extension
tablenames = [filename.removesuffix('.tex').removeprefix('param_')
              for filename in filenames]

if __name__ == '__main__':

    print('Set up:\n')
    print('Database stored in: ' + db_name + '\n')
    print('From manual stored in: ' + manual_path + '\n')
    print('Collecting from the following records: ')
    print(tablenames)
    print()
    print('Parsing private: ' + str(parse_private) + '\n')

    filenames = get_full_manual_paths(filenames, manual_path)
    
    # Parse parameters
    parameters = []
    for filename, tablename in zip(filenames, tablenames):
        parameters.extend(parse_file(filename, 
                                     tablename, 
                                     parse_private, 
                                     manual_path))

    # Create and write into database
    if os.path.exists(db_name):
        os.remove(db_name)
    print(db_name)
    conn = sqlite3.connect(db_name)
    create_tables(conn, tablenames)
    write_parameters(conn, parameters)
    conn.close()

    print('Done.')
