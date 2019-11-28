from Support.database_functions import load_database_table

DATABASE_NAME_COL = 0
DATABASE_SHORT_DESC_COL = 1
DATABASE_LONG_DESC_COL = 2
DATABASE_TYPE_COL = 3
DATABASE_DEFAULT_VALUE_COL = 4
DATABASE_RANGE_COL = 5
DATABASE_BASIC_COL = 6


def get_cell_text(table_row, column_index):
    if len(table_row) >= column_index:
        return table_row[column_index].rstrip().lstrip()
    return ""


def get_name(table_row):
    return get_cell_text(table_row, DATABASE_NAME_COL)


def get_short_desc(table_row):
    return get_cell_text(table_row, DATABASE_SHORT_DESC_COL)


def get_long_desc(table_row):
    return get_cell_text(table_row, DATABASE_LONG_DESC_COL)


def get_type(table_row):
    return get_cell_text(table_row, DATABASE_TYPE_COL)


def get_range(table_row):
    return get_cell_text(table_row, DATABASE_RANGE_COL)


def get_basic(table_row):
    return get_cell_text(table_row, DATABASE_BASIC_COL)


def get_default_value(table_row):
    return get_cell_text(table_row, DATABASE_DEFAULT_VALUE_COL)


def is_logical(table_row):
    if "logical" in get_type(table_row):
        return True
    else:
        return False


def get_default_value_for_name(table, name):
    for table_row in table:
        if get_name(table_row) == name:
            return get_default_value(table_row)
    return ""


def get_basics(table):
    basic_list = list()
    for table_row in table:
        if get_basic(table_row) == "T":
            basic_list.append(table_row)
    return basic_list


def get_advanced(table):
    adv_list = list()
    for table_row in table:
        if get_basic(table_row) != "T":
            adv_list.append(table_row)
    return adv_list


def has_comment(row_type) -> bool:
    """
    return true, if row type contains "--"
    false, else
    :param row_type:
    :return: bool
    """
    if "--" in row_type:
        return True
    else:
        return False


def is_obligatory_if(row_type) -> bool:
    """
    return true, if row type contains "-- (obligatory if"
    false, else
    :param row_type:
    :return: bool
    """
    if "-- (obligatory if" in row_type:
        return True
    else:
        return False


def filter_obligatory(row_type) -> str:
    row_type = row_type.replace("-- (obligatory if", "")
    row_type = row_type.replace("(", "")
    row_type = row_type.replace(")", "").lstrip().rstrip()
    return row_type


def split_parametername_value(parname_and_value):
    return parname_and_value.split("=")


def get_parametername(parname_and_value):
    str_split = split_parametername_value(parname_and_value)
    return str_split[0]


def get_parametervalue(parname_and_value):
    str_split = split_parametername_value(parname_and_value)
    return str_split[1]


def get_obligatory_if_list(table):
    obligatory_pars = list()
    for db_row in table:
        default_value = get_default_value(db_row)
        if is_obligatory_if(default_value):
            parname_and_value = filter_obligatory(default_value)
            par_name = get_parametername(parname_and_value)
            if par_name not in obligatory_pars:
                obligatory_pars.append(par_name)
    return obligatory_pars


def get_all_index_vars(table):
    index_vars_list = list()
    for db_row in table:
        type_value = get_type(db_row)
        if "index variable" in type_value:
            index_vars = type_value[type_value.index("(")+1: type_value.index(
                ")")]
            for index_var in index_vars.split(","):
                index_var = index_var.strip()
                if index_var not in index_vars_list:
                    index_vars_list.append(index_var)
    return index_vars_list


def get_index_vars_for_par(table, par_name):
    index_vars_list = list()
    for db_row in table:
        if par_name is get_name(db_row):
            type_value = get_type(db_row)
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


class DatabaseTable:
    def __init__(self, database_file, table_name):
        self.table = load_database_table(database_file,
                                         table_name)

    def get_table(self):
        return self.table
