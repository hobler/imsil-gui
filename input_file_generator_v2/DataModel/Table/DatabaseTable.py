from Support.database_functions import load_database_table

# The Column indices for the database entries
DATABASE_NAME_COL = 0
DATABASE_SHORT_DESC_COL = 1
DATABASE_LONG_DESC_COL = 2
DATABASE_TYPE_COL = 3
DATABASE_DEFAULT_VALUE_COL = 4
DATABASE_RANGE_COL = 5
DATABASE_BASIC_COL = 6


class DatabaseTable:
    """
    Holds data of a given table in a database and contains methods to 
    get specific type of data.

    Methods:
        :__get_cell_text__: return text in specified table row & column
        :get_name: return the name of the parameter
        :get_short_desc: return the short description of the parameter
        :get_long_desc: return the long description of the parameter
        :get_type: return the type of the parameter
        :get_default_value: return the default value of the parameter
        :get_range: return the range of the parameter
        :get_basic: return all parameters that are marked as basic
        :get_table: return the table itself
        :get_rows: return a list holding all rows of the database
        :get_all_index_vars: return all index array variables from the 
                             database table                         
        :get_index_vars_for_par: return all index variables for the 
            specified parameter
        :is_logical: return True if the parameter is a boolean
        :is_index_var: return True if the parameter is an index 
                       variable array
        :regroup: regroup all parameters in three categories
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
    
    def get_default_value(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_DEFAULT_VALUE_COL)

    def get_range(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_RANGE_COL)

    def get_basic(self, table_row):
        return self.__get_cell_text__(table_row, DATABASE_BASIC_COL)

    def get_table(self):
        return self.table
    
    def get_rows(self):    
        rows_list = []
        # Append every row/parameter of the database to the list
        for table_row in self.table:    
            rows_list.append(table_row) 
        return rows_list

    def get_all_index_vars(self):
        index_vars_list = []
        # Iterate through every row/parameter of the current table
        for db_row in self.table:
            type_value = self.get_type(db_row)
            # If the parameter is an index variable add it to the list. 
            # The type_value has a format of: "index variable array
            # (name_of_parameters) of datatype_of_parameter"
            if self.is_index_var(db_row):
                # Retrieve the name of the parameter(s)
                index_vars = type_value[type_value.index("(")+1:
                                        type_value.index(")")]
                # Iterate through every parameter
                for index_var in index_vars.split(","):
                    index_var = index_var.strip() # Remove whitespaces
                    # Add the element to the list
                    if index_var not in index_vars_list:
                        index_vars_list.append(index_var)                   
        return index_vars_list


    def get_index_vars_for_par(self, par_name):
        index_vars_list = []
        # Iterate through every row/parameter of the current table
        for db_row in self.table:
            # Only check for the specified parameter
            if par_name is self.get_name(db_row):
                type_value = self.get_type(db_row)
                if self.is_index_var(db_row):
                    # Retrieve the name of the parameter(s)
                    index_vars = type_value[type_value.index("(")+1:
                                            type_value.index(")")]
                    # Iterate through every parameter
                    for index_var in index_vars.split(","):
                        index_var = index_var.strip() # Remove whitespaces
                        # Add the element to the list
                        if index_var not in index_vars_list:
                            index_vars_list.append(index_var)
                break # Only check specified parameter
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
                
        bool_table = []
        entry_table = []
        index_table = []
        
        # Iterate through every row and append the entries to the 
        # corresponding list.
        for row in table:
            if self.is_logical(row):
                bool_table.append(row)
            elif self.is_index_var(row):
                index_table.append(row)
            else:
                entry_table.append(row)
              
        # Rearrange the list so the boolean values come first, followed
        # by the entries and finally the index variable arrays                
        entry_table.extend(index_table)
        bool_table.extend(entry_table)
        
        return bool_table
        
        
        
        