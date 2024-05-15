from xml.etree.cElementTree import parse

from adtrees.adnode import ADNode
from util.util import clean_tla_identifier


def file_to_dict(path):
    """
    Path to an ADTool .xml output file --> dictionary for the ADTree creation.
    """
    try:
        with open(path, "rt") as f:
            tree = parse(f)
    except FileNotFoundError:
        raise (
            "Couldn't load ADTree from {}\nThere is no such file or directory.".format(
                path
            )
        )

    tree_root = tree.getroot()[0]
    pt = "a"  # the root is assumed to be of the attacker's type

    # unvisited_et[i] corresponds to the unvisited_adt_nodes[i]
    unvisited_et = [tree_root]
    unvisited_adt_nodes = [get_ad_node(tree_root, pt)]

    d = {unvisited_adt_nodes[0]: []}

    while unvisited_adt_nodes:
        # take the first of the nodes that are left
        current_et = unvisited_et.pop(0)
        current_ad_node = unvisited_adt_nodes.pop(0)

        # take its children in the ET, turn them into ADNodes,
        # add them to the ADTree's dictionary and to the two lists of nodes left to deal with
        pt = current_ad_node.type
        for child in current_et:
            if child.tag == "node":
                ad_node_child = get_ad_node(child, pt)
                # modify the dictionary and the lists
                d[current_ad_node].append(ad_node_child)
                d[ad_node_child] = []
                unvisited_et.append(child)
                unvisited_adt_nodes.append(ad_node_child)

    return d


def get_ad_node(et, pt):
    """
    pt = parent type, 'a' or 'd'
    """
    types = ["a", "d"]

    # the first child is the label, i.e., ETnode[0].tag = 'label'
    label = clean_tla_identifier(et[0].text)

    # the first three children are either
    # label parameter
    # or
    # label parameter node
    # or
    # label node node
    #
    # If any of the two first cases occurs, we are dealing with a basic event node.

    children = [ch for ch in list(et) if "switchRole" not in ch.attrib]

    if len(children) <= 2 or et[1].tag == "parameter":
        ref = None
    else:
        ref = et.attrib["refinement"]
        if ref == "conjunctive":
            ref = "AND"
        else:
            ref = "OR"

    # type
    if "switchRole" in et.attrib:
        # this means that switchRole = "yes"; this node counters its parent
        # for us, this means that an INH node is formed between et (this node) and its parent
        t = types[(types.index(pt) + 1) % 2]
    else:
        t = pt
    return ADNode(actor=t, label=label, refinement=ref)


def get_basic_assignment_xml(path):
    """
    Path to an ADTool .xml output file --> dictionary containing the basic assignment.
    """
    try:
        with open(path, "rt") as f:
            tree = parse(f)
    except FileNotFoundError:
        print(
            "Couldn't load the basic assignment from {}\nThere is no such file or directory.".format(
                path
            )
        )
        return

    real_root = tree.getroot()[0]
    result = {}
    unvisited_et = [real_root]

    while unvisited_et:
        current_et = unvisited_et[0]
        if len(list(current_et)) > 1 and current_et[1].tag == "parameter":
            label = clean_tla_identifier(current_et[0].text)
            if label not in result:
                val = current_et[1].text  # val most probably looks like "10.0"
                result[label] = float(val)  # int(val.split('.')[0])

        for child in current_et:
            if child.tag == "node":
                unvisited_et.append(child)

        unvisited_et.pop(0)

    return result
