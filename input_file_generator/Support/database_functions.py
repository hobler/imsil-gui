import sqlite3


def run_query(database, query, parameters=()) -> list:
    """
    This function opens a connection to the SQLite database file *database*
    and run the *query* that is given as a string. Optionally parameters can
    be given as a tuple.
    """
    conn = None
    query_result = None
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        query_result = cursor.execute(query, parameters).fetchall()
    except sqlite3.Error as e:
        print("Error in run_query: {}".format(e.args[0]))
    finally:
        if conn:
            conn.close()

    return query_result


def load_database_table(database, table, list_where=None) -> list:
    """
    This function loads the content of the SQLite database file *database*
    for a specific *table*. list_where is a list of strings which will be
    placed to the WHERE clause.
    """
    if list_where is None:
        list_where = list()
    query = "SELECT * FROM " + table
    for i in range(len(list_where)):
        if i == 0:
            query = query + " WHERE " + list_where[i]
        else:
            query = query + " AND " + list_where[i]
    query_result = run_query(database, query)
    return query_result
