from __future__ import annotations

import random
import xml.etree.ElementTree as ET

from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment
from utils.util import generate_random_string


def create_tree(max_nodes):
    """
    Creates a random attack defense tree structure with a maximum number of nodes.
    """
    root = ET.Element("adtree")
    total_nodes = 0

    filename = f"./data/random_trees/tree_{f"{max_nodes:02d}"}_{generate_random_string(length=5)}.xml"
    print(f"\n{filename}")

    def create_node(parent, is_counter=False, reserved=0):
        nonlocal total_nodes

        if total_nodes + reserved > max_nodes:
            return

        is_root = total_nodes == 0

        total_nodes = total_nodes + 1

        # Randomly set if it's an AND or OR node
        node = ET.SubElement(parent, "node")

        if is_counter:
            node.set("switchRole", "yes")

        # We need to add at least two children, hence the + 2
        min_children = 2

        occupied_nodes = total_nodes + reserved + min_children

        # Randomly decide the number of children, according to how many total_nodes there are
        # and how many children stil need to be created
        # If we are at the root node, we always create children
        children_prob = random.random() < 1 - (occupied_nodes / max_nodes)
        have_children = is_root or (occupied_nodes <= max_nodes and children_prob)

        if have_children:
            # max_children = int(max(min_children, (max_nodes-total_nodes)/5))
            max_children = min(4, max_nodes - total_nodes)
            children_count = random.randint(min_children, max_children)

            node_type = random.choice(["disjunctive", "conjunctive"])

            label = ET.SubElement(node, "label")
            label.text = (
                f"{"OR" if node_type == "disjunctive" else "AND"}_{total_nodes}"
            )

            print(
                f"{label.text}, max_nodes: {max_nodes}, current_nodes: {total_nodes}, reserved: {reserved}, add_children: {children_count}",
            )

            node.set("refinement", node_type)
            child_is_counter = False
            has_been_countered = False

            # We want that only a single child counters this node,
            # with probability of 20%, only if there is space for one more node
            i = 0
            while i < children_count:
                child_is_counter = (
                    not child_is_counter
                    and total_nodes + reserved + 1 <= max_nodes
                    and random.random() < 0.2
                )

                if child_is_counter:
                    if children_count == 2:
                        children_count += 1

                    reserved += 1

                create_node(
                    node,
                    not has_been_countered and child_is_counter,
                    reserved + (children_count - i - 1),
                )

                if child_is_counter:
                    has_been_countered = True

                i += 1
        else:
            node.set("refinement", "")

            label = ET.SubElement(node, "label")
            label.text = f"BS_{total_nodes}"

            parameter = ET.SubElement(node, "parameter")
            parameter.set("domainId", "MinCost1")
            parameter.set("category", "basic")
            parameter.text = str(random.randint(1, int(1e5)))

    # Start building the tree
    create_node(root)

    # Add domain element
    domain = ET.SubElement(root, "domain")
    domain.set("id", "MinCost1")
    sub_domain = ET.SubElement(domain, "class")
    sub_domain.text = "lu.uni.adtool.domains.adtpredefined.MinCost"
    sub_tool = ET.SubElement(domain, "tool")
    sub_tool.text = "ADTool2"

    # Convert the tree to a string and print
    xml_tree = ET.ElementTree(root)
    ET.indent(xml_tree, space="  ", level=0)
    xml_tree.write(filename)

    # Check if the tree is correct
    tree = ADTree(filename)
    ba = BasicAssignment(filename)
    for s in tree.get_basic_actions():
        ba[s]


if __name__ == "__main__":
    for i in range(4, 75):
        for _ in range(3):
            create_tree(max_nodes=i)
