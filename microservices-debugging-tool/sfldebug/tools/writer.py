import os
import json
from typing import Any, List

import sfldebug.tools.logger as sfl_logger


class SetEncoder(json.JSONEncoder):
    """Simple set encoder to transform sets into list when encoding to json"""

    def default(self, o: Any) -> Any:
        if isinstance(o, set):
            return list(o)
        return json.JSONEncoder.default(self, o)


def write_results_to_file(
    json_body: dict | List,
    filename: str,
    execution_id: str,
    indent: int = 2
) -> None:
    """Writes results into a file in a 'results' folder located in the project directory.
    Converts dict objects into a json file.
    If the file/folders do not exist, they are created.

    Args:
        json_body (dict | List): dict body to be written in the json file
        filename (str): name of the file to be written
        execution_id (str): id of the execution to sort results from different executions
        indent (int, optional): file indentation. Defaults to 2.
    """
    project_dir = os.path.join(os.getcwd(), 'results', execution_id)
    os.makedirs(project_dir, exist_ok=True)

    filename += '.json' if not filename.endswith('.json') else ''
    with open(os.path.join(project_dir, filename), 'w', encoding='utf-8') as file:
        file.write(json.dumps(json_body, indent=indent, cls=SetEncoder))
    sfl_logger.logger.info('Data wrote to: %s. Execution ID: <%s>.',
                           filename, execution_id)
