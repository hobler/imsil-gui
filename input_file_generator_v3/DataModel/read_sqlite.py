"""
Read data from an SQLite database.

Functions:
    `get_database_table_names`
        Get the names of the database tables.

Classes:
    `DatabaseTable`
        Represents one table in the database.
"""
import sqlite3

# Constants for the master tables
DATABASE_SQLITE_MASTER_TABLE_NAME = "sqlite_master"

DATABASE_TYPE_COL = 0
DATABASE_NAME_COL = 1
DATABASE_TBL_NAME_COL = 2
DATABASE_ROOTPAGE_COL = 3
DATABASE_SQL_COL = 4

# Column indices for the database entries
DATABASE_NAME_COL = 0
DATABASE_SHORT_DESC_COL = 1
DATABASE_LONG_DESC_COL = 2
DATABASE_TYPE_COL = 3
DATABASE_DEFAULT_VALUE_COL = 4
DATABASE_RANGE_COL = 5
DATABASE_BASIC_COL = 6


def _run_query(database, query):
    """
    Open a connection to an SQLite database and run a query.

    :param database: filename of the database
    :param query: SQLite query string
    :return: list of table rows
    """
    conn = None
    table_rows = None
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        table_rows = cursor.execute(query).fetchall()
    except sqlite3.Error as e:
        print("Error in run_query: {}".format(e.args[0]))
    finally:
        if conn:
            conn.close()

    return table_rows


def _load_database_table(database, table, conditions=None):
    """
    This function loads the content of the SQLite database file *database*
    for a specific *table*. list_where is a list of strings which will be
    placed to the WHERE clause.
    :param database: filename of the database
    :param table: table to be loaded from database database
    :param conditions: list of conditions to be passed in WHERE clauses
    :return: list of table rows
    """
    query = "SELECT * FROM " + table

    if conditions is None:
        conditions = list()
    for i, condition in enumerate(conditions):
        if i == 0:
            query += " WHERE " + condition
        else:
            query += " AND " + condition

    table_rows = _run_query(database, query)

    return table_rows


def get_database_table_names(db_file):
    """
    Retrieve the names of the database tables.

    :param db_file: Name of the database file.
    :return: Table names
    """
    table_rows = _load_database_table(db_file,
                                      DATABASE_SQLITE_MASTER_TABLE_NAME,
                                      ["type='table'"])
    table_names = list()
    for table_row in table_rows:
        table_names.append(table_row[DATABASE_TBL_NAME_COL])

    return table_names


class DatabaseTable:
    """
    One table in a database.

    Methods:
        :get_name: return the name of the parameter
        :get_short_desc: return the short description of the parameter
        :get_long_desc: return the long description of the parameter
        :get_type: return the type of the parameter
        :get_default_value: return the default value of the parameter
        :get_range: return the range of the parameter
        :get_basic: return all parameters that are marked as basic
        :get_rows: return a list holding all rows of the database
#        :get_all_index_vars: return all index array variables from the
#                             database table
        :get_index_vars_for_par: return all index variables for the
            specified parameter
        :is_logical: return True if the parameter is a boolean
        :is_index_var: return True if the parameter is an index
                       variable array
        :regroup: regroup all parameters in the three categories
    """

    def __init__(self, database_file, table_name):
        self.table = _load_database_table(database_file, table_name)

    @staticmethod
    def _get_cell_text(table_row, column_index):
        """Return text in as specific table row and column."""
        if len(table_row) >= column_index:
            return table_row[column_index].rstrip().lstrip()
        return ""

    def get_name(self, table_row):
        return self._get_cell_text(table_row, DATABASE_NAME_COL)

    def get_short_desc(self, table_row):
        return self._get_cell_text(table_row, DATABASE_SHORT_DESC_COL)

    def get_long_desc(self, table_row):
        return self._get_cell_text(table_row, DATABASE_LONG_DESC_COL)

    def get_type(self, table_row):
        return self._get_cell_text(table_row, DATABASE_TYPE_COL)

    def get_default_value(self, table_row):
        return self._get_cell_text(table_row, DATABASE_DEFAULT_VALUE_COL)

    def get_range(self, table_row):
        return self._get_cell_text(table_row, DATABASE_RANGE_COL)

    def get_basic(self, table_row):
        return self._get_cell_text(table_row, DATABASE_BASIC_COL)

    def get_rows(self):
        # table is already a list of rows
        return self.table

    #    def get_all_index_vars(self):
    #        index_vars_list = []
    #        # Iterate through every row/parameter of the current table
    #        for db_row in self.table:
    #            type_value = self.get_type(db_row)
    #            # If the parameter is an index variable add it to the list.
    #            # The type_value has a format of: "index variable array
    #            # (name_of_parameters) of datatype_of_parameter"
    #            if self.is_index_var(db_row):
    #                # Retrieve the name of the parameter(s)
    #                index_vars = type_value[type_value.index("(")+1:
    #                                        type_value.index(")")]
    #                # Iterate through every parameter
    #                for index_var in index_vars.split(","):
    #                    index_var = index_var.strip() # Remove whitespaces
    #                    # Add the element to the list
    #                    if index_var not in index_vars_list:
    #                        index_vars_list.append(index_var)
    #        return index_vars_list

    def get_index_vars_for_par(self, par_name):
        index_vars_list = []
        # Iterate through every row/parameter of the current table
        for db_row in self.table:
            # Only check for the specified parameter
            if par_name is self.get_name(db_row):
                type_value = self.get_type(db_row)
                if self.is_index_var(db_row):
                    # Retrieve the name(s) of the index variable(s).
                    # The type_value variable has a format of:
                    # "index variable array (index variables) of
                    # datatype_of_parameter"
                    index_vars = type_value[type_value.index("(") + 1:
                                            type_value.index(")")]
                    # Iterate through every parameter
                    for index_var in index_vars.split(","):
                        index_var = index_var.strip()  # Remove blanks
                        # Add the element to the list
                        if index_var not in index_vars_list:
                            index_vars_list.append(index_var)
                break  # Only check specified parameter
        return index_vars_list

    def is_logical(self, table_row):
        if "logical" in self.get_type(table_row):
            return True
        else:
            return False

    def is_index_var(self, table_row):
        if "index variable" in self.get_type(table_row):
            return True
        else:
            return False

    def regroup(self):
        # Sort the list alphabetically
        self.table.sort()

        # Create empty lists for all of the categories
        bool_table = []
        entry_table = []
        index_table = []

        # Iterate through every row and append the entries to the
        # corresponding list
        for row in self.table:
            if self.is_logical(row):
                bool_table.append(row)
            elif self.is_index_var(row):
                index_table.append(row)
            else:
                entry_table.append(row)

        # Overwrite the table so the boolean values come first, followed
        # by the entries and finally the index variable arrays
        self.table = bool_table + entry_table + index_table
