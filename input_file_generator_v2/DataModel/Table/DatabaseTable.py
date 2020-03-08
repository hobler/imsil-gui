from Support.database_functions import load_database_table

DATABASE_NAME_COL = 0
DATABASE_SHORT_DESC_COL = 1
DATABASE_LONG_DESC_COL = 2
DATABASE_TYPE_COL = 3
DATABASE_DEFAULT_VALUE_COL = 4
DATABASE_RANGE_COL = 5
DATABASE_BASIC_COL = 6


class DatabaseTable:
    """
    Hold data of a given table in a database and contains methods to get
    specific type of data.

    Methods:
        :__get_cell_text__: return text in specified table row and column
        :get_all_index_vars: return all index variables from the database table
        :get_basics: return all parameters that are marked as basic
        :get_advanced: return all parameters that are not marked as basic
        :get_index_vars_for_par: return all index variables for specified
            parameter name
    """
    def __init__(self, database_file, table_name):
        self.table = load_database_table(database_file, table_name)

    @staticmethod
    def __get_cell_text__(table_row, column_index):
        if len(table_row) >= column_index:
            return table_row[column_index].rstrip().lstrip()
        return ""

    def get_name(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_NAME_COL)

    def get_short_desc(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_SHORT_DESC_COL)

    def get_long_desc(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_LONG_DESC_COL)

    def get_type(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_TYPE_COL)

    def get_range(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_RANGE_COL)

    def get_basic(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_BASIC_COL)

    def get_default_value(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_DEFAULT_VALUE_COL)

    def get_table(self):
        return self.table

    def get_all_index_vars(self):
        index_vars_list = list()
        for db_row in self.table:
            type_value = self.get_type(db_row)
            if "index variable" in type_value:
                index_vars = type_value[type_value.index("(")+1:
                                        type_value.index(")")]
                for index_var in index_vars.split(","):
                    index_var = index_var.strip()
                    if index_var not in index_vars_list:
                        index_vars_list.append(index_var)
        return index_vars_list

    def get_rows(self):
        rows_list = list()
        for table_row in self.table:    
            rows_list.append(table_row)
        return rows_list

    def get_index_vars_for_par(self, par_name):
        index_vars_list = list()
        for db_row in self.table:
            if par_name is self.get_name(db_row):
                type_value = self.get_type(db_row)
                if "index variable" in type_value \
                        and "(" in type_value and ")" in type_value:
                    index_vars = type_value[type_value.index("(")+1:
                                            type_value.index(")")]
                    for index_var in index_vars.split(","):
                        index_var = index_var.strip()
                        if index_var not in index_vars_list:
                            index_vars_list.append(index_var)
                return index_vars_list
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

    def regroup(self, table):
        # Sort the list alphabetically
        table = sorted(table)
        
        # Rearrange the list so the boolean values come first, followed
        # by the entries and finally the index variable arrays
        bool_table = []
        entry_table = []
        index_table = []
        
        # Iterate through every row and append the entries to the 
        # correct table.
        for row in table:
            if self.is_logical(row):
                bool_table.append(row)
            elif self.is_index_var(row):
                index_table.append(row)
            else:
                entry_table.append(row)
               
        # Merges the tables together in the right order and return them
        entry_table.extend(index_table)
        bool_table.extend(entry_table)
        
        return bool_table
        
        
        
        