import json
import os

def file(path):
    """
    Return absolute path for a file.

    Arguments:
        path: The path to get the OS path for.
    Returns:
        A file path.
    """
    return os.path.abspath(path)

def load_api_key(key_file, json_key):
    """
    Loads the API key for The Blue Alliance.

	Arguments:
		key_file: The file name for the file with the authentication key.
		json_key: The dictionary key value for the authentication key.
    Returns:
        A string
    """
    with open(key_file) as key_json_file:
        key_obj = json.load(key_json_file)
        return key_obj[json_key]
