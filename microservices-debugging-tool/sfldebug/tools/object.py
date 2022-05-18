# pylint: disable=anomalous-backslash-in-string
import re
from typing import Any, List, Optional


def extract_filename(filepath: str) -> str:
    """Extract the name of the file from the file path.

    Args:
        filepath (str): full or relative path of a file

    Returns:
        str: name of the file (extension excluded)
    """
    unix_match = re.search('.*?/?(\\w[\\w|-]+)\\.\\w+', filepath, re.IGNORECASE)
    windows_match = re.search('.*?[\\\\]?(\\w[\\w|-]+)\\.\\w+', filepath, re.IGNORECASE)
    if unix_match is not None:
        return unix_match.group(1)
    if windows_match is not None:
        return windows_match.group(1)
    return ''


def extract_field(
    field: str,
    obj: Any
) -> Optional[Any]:
    """Simple field extraction function that returns none if the field is not present in the object.

    Args:
        field (str): name of the field to be extracted
        obj (Any): object to extract the data

    Returns:
        Any|None: returns the contents in the field, if present, or None, if missing
    """
    if field in obj:
        return obj[field]
    return None


def merge_lists(
    new_list: List[Any],
    old_list: List[Any]
) -> List[Any]:
    """Merge lists without type checking the lists contents.

    Args:
        new_list (List[Any]): new list to be merged
        old_list (List[Any]): old list to be merged

    Returns:
        List[Any]: merged list of list
    """
    if new_list is None:
        return old_list
    if old_list is None:
        return new_list

    merged_list = old_list + new_list
    return merged_list


def make_list(obj: Any) -> List[Any]:
    """Simple converter of a obj to obj list.
    If the obj is already list, returns itself.
    If obj is None, return an empty list.

    Args:
        obj (Any): obj to be converted to a list

    Returns:
        List[Any]: list of obj
    """
    if isinstance(obj, list):
        return obj
    if isinstance(obj, (tuple, set)):
        return list(obj)
    if obj is None:
        return []
    return [obj]


def merge_into_list(
    obj1: Any,
    obj2: Any
) -> List[Any]:
    """Merge two objects into a single list.
    First convert each obj into a list and then merge them.

    Args:
        obj1 (Any): first object to be merged into list
        obj2 (Any): second object to be merged into list

    Returns:
        List[Any]: list of the merged object lists
    """
    obj1_list = make_list(obj1)
    obj2_list = make_list(obj2)

    return merge_lists(obj1_list, obj2_list)


def cmp_entities(
    ent1: dict,
    ent2: dict
) -> int:
    """Custom comparator for entities rankings.
    It is assumed the ranking is associated to key 'entity_rank'

    Args:
        ent1 (dict): Entity ranking to be compared
        ent2 (dict): Other entity ranking to be compared

    Returns:
        int: 1 if ent1 has lower ranking, -1 if ent1 has higher ranking,
        0 if both rankings are equal
    """
    rank1 = ent1['entity_rank']
    rank2 = ent2['entity_rank']

    if rank1 < rank2:
        return 1
    if rank1 > rank2:
        return -1
    return 0


def cmp_deltas(
    eval1: dict,
    eval2: dict
) -> int:
    """Custom comparator for entities rankings deltas.
    It is assumed the ranking delta is associated to key 'delta_entity'

    Args:
        eval1 (dict): Entity ranking delta to be compared
        eval2 (dict): Other entity ranking delta to be compared

    Returns:
        int: 1 if eval1 has lower delta, -1 if eval1 has higher delta,
        0 if both deltas are equal
    """
    rank1 = eval1['delta_entity']
    rank2 = eval2['delta_entity']

    if rank1 > rank2:
        return 1
    if rank1 < rank2:
        return -1
    return 0
