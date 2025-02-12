"""
Database Module based on micropython's btree

The btree module implements a simple key-value
database using external storage (disk files, or
in general case, a random-access stream).
Keys are stored sorted in the database, and
besides efficient retrieval by a key value,
a database also supports efficient ordered
range scans (retrieval of values with the
keys in a given range).

User can define and store an external storage
binary file (database_file) to use as a custom database.
"""

import btree


def get_inventory(database_file):
    """ Returns total .

    Parameters:
        database_file {str}: selected database file

    Returns:
        (int) total count
    """
    with open(database_file, "r+b") as file:
        db = btree.open(file, minkeypage = 100)
        value_list = list(db.keys())
        _count = len(value_list)
        db.flush()
        db.close()
    return _count


def get_value(database_file):
    """ Returns the first value under a specific
        key from the given database.

    Parameters:
        database_file {str}: selected database file

    Returns:
        value (bytes): the value under the key
    """
    # if the database file does not exist
    # a database needs to be created.
    try:
        file = open(database_file, "r+b")
    except OSError:
        file = open(database_file, "w+b")
    db = btree.open(file, minkeypage = 100)
    _list = list(db.keys())
    # if database is not empty get value
    if _list != []:
        _key = _list.pop(0)
        value = db.get(_key)
        del db[_key]
    else:
        value = b''
    db.flush()
    db.close()
    file.close()
    return value


def update_database(data, database_file):
    """ updates database with the given data.

    Parameters:
        data (tuple):  tuple of values
        database_file (str): selected database file

    Returns:
        status (bool): True for success False for failure.
    """
    with open(database_file, "r+b") as file:
        db = btree.open(file, minkeypage = 100)
        # if database is empty start database key at 0 else
        # continue by incrementing from previous key
        try:
            _key = max([int(x) for x in db.keys()])
        except ValueError:
            _key = 0
        # add each value to the database
        for value in data:
            _key += 1
            db[str(_key)] = value
        db.flush()
        db.close()
    return True


def clean_database(database_file):
    """ Erase all data under a database.

    Parameters:
        database_file {str}: selected database file

    Returns: None
    """
    try:
        file = open(database_file, "r+b")
    except OSError:
        print(f'{database_file} Does not exist!')
        return
    db = btree.open(file, minkeypage = 100)
    for key in db:
        del db[key]
    db.flush()
    db.close()
    file.close()
