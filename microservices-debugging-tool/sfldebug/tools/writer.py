import json


def write_json_to_file(json_body: dict, filename: str, indent: int = 2) -> None:
    """Writes dict objects to a json file. If the file does not exist, it is created.
    If the file already exists, it is overwritten.

    Args:
        json_body (dict): dict body to be written in the json file
        filename (str): name of the file to be written
        indent (int, optional): file indentation. Defaults to 2.
    """
    with open(filename + '.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(json_body, indent=indent, sort_keys=True))
    print('Data wrote to: {}.json'.format(filename))
