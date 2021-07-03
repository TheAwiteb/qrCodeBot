import json
from config import JSON_FILE

def get_data():
    """ returns data from json file

    Returns:
        dict: dictionary of data
    """
    with open(JSON_FILE, 'r') as f:
        return json.load(f)

def get_key(key:str):
    """ returns value of key

    Args:
        key (str): key you want value for

    Returns:
        any: value of key
    """
    return get_data().get(key)

def push_data(new_data:dict):
    """ change json file data to new_data

    Args:
        new_data (dict): new data
    """
    with open(JSON_FILE, 'w') as f:
        json.dump(new_data, f, indent=4)

def update_data(key:str, new_val:dict):
    """ update key in json file

    Args:
        key (str): key you want update
        new_val (dict): new value for key
    """
    data = get_data()
    data[key] = new_val
    push_data(new_data = data)

def get_values():
    """ returns values of data

    Returns:
        list: list of values
    """
    return get_data().values()