"""
Read data from an SQLite database.

Functions:
    `get_database_table_names`
        Get the names of the database tables.

Classes:
    `DatabaseTable`
        Represents one table in the database.
    `DatabaseTableRow`
        Represents one row in a table in the database.
"""
import sqlite3

# Constants for the master tables
DATABASE_SQLITE_MASTER_TABLE_NAME = 'sqlite_master'

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


def _run_query(db_file, query):
    """
    Open a connection to an SQLite database and run a query.

    :param db_file: (string) filename of the database
    :param query: (string) SQLite query string
    :return: (list of tuples) list of table rows
    """
    conn = None
    table_rows = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        table_rows = cursor.execute(query).fetchall()
    except sqlite3.Error as e:
        print('Error in run_query: {}'.format(e.args[0]))
    finally:
        if conn:
            conn.close()

    return table_rows


def _load_database_table(db_file, table, conditions=None):
    """
    Load a table from an SQLite database.

    :param db_file: (string) filename of the database
    :param table: (string) table to be loaded from database
    :param conditions: (list of strings) list of conditions to be passed to
    WHERE clauses
    :return: (list of tuples) list of table rows
    """
    query = "SELECT * FROM " + table

    if conditions is not None:
        for i, condition in enumerate(conditions):
            if i == 0:
                query += " WHERE " + condition
            else:
                query += " AND " + condition

    table_rows = _run_query(db_file, query)

    return table_rows


def get_database_table_names(db_file):
    """
    Retrieve the names of the database tables.

    :param db_file: (string) Name of the database file
    :return: (list of strings) Table names
    """
    table_rows = _load_database_table(db_file,
                                      DATABASE_SQLITE_MASTER_TABLE_NAME,
                                      ["type='table'"])
    table_names = []
    for table_row in table_rows:
        table_names.append(table_row[DATABASE_TBL_NAME_COL])

    return table_names


class DatabaseTable:
    """
    One table in a database corresponding to an IMSIL 'record'.

    The table is represented by a list of DatabaseTableRow objects.
    Iterating over the DatabaseTable returns DatabaseTableRows.

    Upon initialization, the rows are ordered alphabetically. Optionally,
    the rows may be grouped using the regroup method.
    """

    def __init__(self, db_file, table_name):
        """
        :param db_file: (string) Name of the database file.
        :param table_name: (string) Table name.
        """
        table_row_list = _load_database_table(db_file, table_name)
        table_row_list.sort()
        self.table_row_list = []
        for table_row in table_row_list:
            self.table_row_list.append(DatabaseTableRow(table_row))
        self.table_name = table_name

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= len(self.table_row_list):
            raise StopIteration
        else:
            table_row = self.table_row_list[self.index]
            self.index += 1
            return table_row

    def regroup(self):
        """
        Regroup the table rows.

        Regroup the table rows so booleans come first followed by entries and
        index variable arrays.
        """
        bool_list = []
        entry_list = []
        index_list = []
        for table_row in self.table_row_list:
            if table_row.is_logical():
                bool_list.append(table_row)
            elif table_row.is_index_var():
                index_list.append(table_row)
            else:
                entry_list.append(table_row)
        self.table_row_list = bool_list + entry_list + index_list


class DatabaseTableRow:
    """
    One row in a database table corresponding to an IMSIL 'parameter'.
    """
    def __init__(self, table_row):
        """
        :param table_row: (tuple of strings) Table row
        """
        self.table_row = table_row

    def _get_cell_text(self, column_index):
        """Return text in a specific table column."""
        if column_index < len(self.table_row):
            return self.table_row[column_index].rstrip().lstrip()
        else:
            return ""

    def get_name(self):
        """Return the name of the parameter."""
        return self._get_cell_text(DATABASE_NAME_COL)

    def get_short_desc(self):
        """Return the short description of the parameter."""
        return self._get_cell_text(DATABASE_SHORT_DESC_COL)

    def get_long_desc(self):
        """Return the long description of the parameter."""
        return self._get_cell_text(DATABASE_LONG_DESC_COL)

    def get_type(self):
        """Return the type of the parameter."""
        return self._get_cell_text(DATABASE_TYPE_COL)

    def get_default_value(self):
        """Return the default value of the parameter"""
        return self._get_cell_text(DATABASE_DEFAULT_VALUE_COL)

    def get_range(self):
        """Return the range of the parameter"""
        return self._get_cell_text(DATABASE_RANGE_COL)

    def get_basic(self):
        """Return the basic flag of the parameter."""
        return self._get_cell_text(DATABASE_BASIC_COL)

    def get_index_vars(self):
        """Return a list of index variables for the parameter."""
        index_vars_list = []
        type_value = self.get_type()
        if self.is_index_var():
            # Retrieve the name(s) of the index variable(s).
            # The type_value variable has a format of:
            # "index variable array (index variables) of datatype_of_parameter"
            index_vars = type_value[type_value.index("(") + 1:
                                    type_value.index(")")].split(",")
            # Iterate through every index variable
            for index_var in index_vars:
                index_var = index_var.strip()  # Remove blanks
                # Add the element to the list avoiding duplicates
                if index_var not in index_vars_list:
                    index_vars_list.append(index_var)
        return index_vars_list

    def is_logical(self):
        """Check if the parameter is a boolean"""
        return "logical" in self.get_type()

    def is_index_var(self):
        """Check if the parameter is an index variable array."""
        return "index variable" in self.get_type()
