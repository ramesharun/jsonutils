"""Convert dict objects from json_lws to pretty print strings.

"""

from collections import defaultdict

# Print Helpers

def is_iter(arg):
    """Return True if argument is iterable."""
    return isinstance(arg, list) or isinstance(arg, tuple)

def format_node(node, indent, depth, to_str=str):
    """Return string of graph node based on arguments.
    Args
        node: string of node to print
        indent: string of tree indentation chars
        depth: int of tree depth, 0 = root
        to_str: function to convert node to string, by default str
    Returns
        Formatted string.
    """
    space = ' ' * ((len(indent) + 1) * (depth - 1))
    leader = '|' + indent if depth > 0 else ''
    return space + leader + to_str(node)

# Data Helpers

def flatten_list(nested):
    """Accepts arbitrarily nested lists and returns generator for flat list."""
    for outer in nested:
        if isinstance(outer, list):
            for inner in flatten_list(outer):
                yield inner
        else:
            yield outer

def filter_errors(vals, error):
    """Helper for filter_keys.
    Return single value from list of values if a non-error term exists; else
    return the error term.
    """
    return (vals[0] if len(vals) == 1 else
            error if set(vals) == {error} else
            [v for v in vals if v != error][0])

def filter_keys(pairs, error):
    """Take list of (key, value) tuples and filter out redundant values.
    For every key, all error values are redundant if there is a non-error value.
    Args
        pairs: list of (key, value) tuples
        error: error value to match values against
    Returns
        List of filtered (key, value) tuples; the filtered list should contain
        unique keys only.
    """
    keys = defaultdict(list)
    for pair in pairs:
        fst, snd = pair
        keys[fst].append(snd)

    ret_pairs = []
    for key in keys:
        val = filter_errors(keys[key], error)
        ret_pairs.append((key, val))

    return ret_pairs

def dict_to_tree(d, key, tree, depth=0, error=''):
    """Transform dict into nested list of values representing tree form.
    Dict should be a graph in adjacency list form, i.e. mapping one node to a
    list of one or more nodes. The resulting nested list is in depth-first
    form, with the level of list nesting corresponding to the depth of the
    node(s).
    Args
        d: dict to transform
        key: initial key value ("root" of dict)
        tree: list, initialized as singleton [(root value, 0)]
        error: error value to filter for, optional
    Returns
        Nested list of (value, int of depth) pairs.
    """
    if key not in d:
        return tree
    else:
        keys = filter_keys(d[key], error) if error else d[key]
        return tree + [dict_to_tree(d, x, [(x, depth + 1)], depth + 1)
                       for x in keys]

def gen_log(graph, root, base_tree, node_to_str, error_dict, indent=' -- '):
    """
    Args
        graph
        root
        base_tree
        node_to_str
        error_dict
        indent
    Returns

    """

    tree_list = dict_to_tree(graph, root, base_tree)
    flat_list = list(flatten_list(tree_list))

    output = [format_node(val, indent, depth, node_to_str)
              for val, depth in flat_list]

    return '\n'.join(output)

