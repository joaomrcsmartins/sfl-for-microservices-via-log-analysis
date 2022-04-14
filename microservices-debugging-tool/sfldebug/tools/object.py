from typing import Any, List, Optional


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
    else:
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
    elif isinstance(obj, (tuple, set)):
        return list(obj)
    elif obj is None:
        return []
    else:
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
