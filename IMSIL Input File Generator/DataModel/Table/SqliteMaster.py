from Support.database_functions import load_database_table

DATABASE_SQLITE_MASTER_TABLE_NAME = "sqlite_master"

DATABASE_TYPE_COL = 0
DATABASE_NAME_COL = 1
DATABASE_TBL_NAME_COL = 2
DATABASE_ROOTPAGE_COL = 3
DATABASE_SQL_COL = 4


class SqliteMaster:
    """
        SqliteMaster is used to get all table names from an sqlite database
        file.

        With get_table_names all table names can be taken from the database
        file.
    """
    def __init__(self, db_file):
        self.table = load_database_table(db_file,
                                         DATABASE_SQLITE_MASTER_TABLE_NAME,
                                         ["type='table'"])

    def get_table(self):
        return self.table

    def get_table_names(self):
        table_names = list()
        for table_row in self.get_table():
            table_names.append(table_row[DATABASE_TBL_NAME_COL])
        return table_names
