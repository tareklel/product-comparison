def get_keys_within_key(d, target_key):
    """
    Get all keys within a specific key of a nested dictionary. 
    This gathers keys from all instances of the target key across the tree.

    :param d: The nested dictionary.
    :param target_key: The key within which to get the keys.
    :return: A set of keys within the target key or an empty set if the key is not found.
    """
    # If the current object is not a dictionary, return an empty set.
    if not isinstance(d, dict):
        return set()

    # If the target key exists in the current dictionary, retrieve its keys.
    keys = set(d[target_key].keys()) if target_key in d and isinstance(
        d[target_key], dict) else set()

    # Recurse deeper to find other instances of the target key and aggregate the results.
    for key in d:
        keys |= get_keys_within_key(d[key], target_key)

    return keys


def find_level(data, target_key, level=1):
    """Recursively search for the target_key and return its level."""

    # Ensure that the input data is a dictionary
    if not isinstance(data, dict):
        return None

    # If the target_key is found at the current level, return the level
    if target_key in data:
        return level

    # Recursively search in nested dictionaries
    for key, value in data.items():
        result = find_level(value, target_key, level + 1)

        # If the target_key is found in the nested dictionary, return its level
        if result:
            return result

    # If the target_key is not found, return None
    return None


def count_children(data, level=1, max_level=None, path=[]):
    """Recursively traverse the tree up to the given max_level and count the children."""

    # Return an empty dictionary if the input data is not a dictionary
    # or if the current level exceeds the max_level
    if not isinstance(data, dict) or (max_level and level > max_level):
        return {}

    child_counts = {}

    # Iterate over each key-value pair in the data dictionary
    for key, value in data.items():
        current_path = path + [key]
        branch = '.'.join(current_path)

        # If the current level matches the max_level, count the children
        if level == max_level:
            child_counts[branch] = len(value) if isinstance(value, dict) else 0

        # Merge child counts from lower levels
        child_counts.update(count_children(
            value, level + 1, max_level, current_path))

    return child_counts


def get_grouping(children, divider):
    """Group children based on the specified divider."""

    # Create a set of parent keys using the divider
    parents = set(x.split('.'+divider+'.')
                  [0] + '.' + divider for x in children)

    compared = {}
    for x in parents:
        compared[x] = {}

        # Temporary list to store keys that should be removed from children after processing
        to_pop = []

        # Iterate over each child and group them based on the parent key
        for key, value in children.items():
            if x in key:
                compared[x][key.split(x+'.')[-1]] = value
                to_pop.append(key)

        # Remove processed keys from the children dictionary
        [children.pop(x) for x in to_pop]

    return {k: compared[k] for k in sorted(compared)}


def df_to_nested_dict(df, columns):
    # Base Case: If no more columns are left, return empty string
    if len(columns) == 0:
        return {}

    # Recursive Case
    col = columns[0]
    nested_dict = {}

    for key, group in df.groupby(col):
        remaining_columns = columns[1:]
        if not nested_dict:
            nested_dict[col] = {key: df_to_nested_dict(
                group.drop(columns=[col]), remaining_columns)}
        else:
            nested_dict[col][key] = df_to_nested_dict(
                group.drop(columns=[col]), remaining_columns)

    return nested_dict


def remove_from_tree(d1: dict, d2: dict, level, target_level):
    """traverses both dictionaries level-by-level. 
    When it reaches the target level, it marks keys for deletion from the first dictionary (d1) 
    if they are also present in the second dictionary (d2). 
    Then it proceeds to delete those keys. 
    This process effectively removes the branches from d1 that are specified by d2."""
    keys_to_delete = []
    # Loop through keys in the second dictionary
    for key in d2.keys():

        # If the key is present in the first dictionary
        if key in d1:

            # If the current level matches the target level, mark key for deletion
            if level == target_level:
                keys_to_delete.append(key)
                continue

            # If both values are dictionaries, proceed to the next level
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                remove_from_tree(d1[key], d2[key], level + 1, target_level)

    # Delete marked keys from the first dictionary
    for key in keys_to_delete:
        del d1[key]
