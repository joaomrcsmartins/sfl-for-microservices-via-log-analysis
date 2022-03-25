from typing import Any, List


def extract_field(field: str, obj: Any) -> Any | None:
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


def merge_attributes(new_attribute: List[Any], old_attribute: List[Any]) -> List[Any]:
    """Merge lists of attributes without type checking the lists contents.

    Args:
        new_attribute (List[Any]): new attributes to be merged
        old_attribute (List[Any]): old attributes to be merged

    Returns:
        List[Any]: merged list of attributes
    """
    if new_attribute is None:
        return old_attribute
    if old_attribute is None:
        return new_attribute

    merged_attributes = old_attribute + new_attribute
    return merged_attributes
