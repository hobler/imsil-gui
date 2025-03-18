"""This module provides some basic functions for creating/writing tables

The connection to the database is generally passed along as the first argument
of a function.

An existing .db file can also be edited using the DB Browser for SQLite.
Check README for more information.
"""
from code.parameter import Parameter


def create_tables(conn, table_names):
    """Creates a new database with the given tables.

    :param conn: Connection to the database
    :param table_names: List of all the tables for the new database
    """
    c = conn.cursor()

    for name in table_names:
        query = ("""CREATE TABLE IF NOT EXISTS {} (
                    name text,
                    short_desc text,
                    long_desc text,
                    type text,
                    defaultValue text,
                    range text,
                    condition text
                    )""").format(name)
        c.execute(query)
        conn.commit()


def get_data(conn, table, sort='name'):
    """Retrieve all parameters of table from the database.

    :param conn: Connection to the database
    :param table: Requested table
    :param sort: Attribute used for sorting

    :return: List of Parameter objects
    """
    c = conn.cursor()

    query = ('SELECT * FROM {} ORDER BY {}').format(table, sort)
    c.execute(query)
    entries = c.fetchall()
    parameters = []
    for entry in entries:
        parameters.append(Parameter(table, *entry))

    conn.commit()
    return parameters


def write_parameters(conn, parameters):
    """Write parameters to the database.

    :param conn: Connection to the database
    :param parameters: List of Parameter objects to be stored
    """

    c = conn.cursor()

    for param in parameters:
        query = ('INSERT INTO {} VALUES '.format(param.record) +
                 '(:name, :short_desc, :long_desc, :type, :defaultValue, ' +
                 ':range, :condition)')
        c.execute(query, param.get_dict())
        conn.commit()

