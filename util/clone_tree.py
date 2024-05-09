import os.path
import xml.etree.ElementTree as ET
import secrets
import string
import random


def generate_random_string(length=10):
    # Generate a random string of fixed length
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def modify_labels(xml_path, output_path):
    # Load the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Modify each label element
    labels = root.findall(".//label")
    for label in labels:
        random_string = generate_random_string()
        label.text = random_string

    # Write the modified XML to a new file
    tree.write(output_path)


def merge_trees(tree_path, tree_path_format):
    # Process each of the files from thesis_tree_6_1.xml to thesis_tree_6_9.xml
    for j in range(0, 8):
        # Load the original tree fresh for each modification
        original_tree = ET.parse(tree_path)
        original_root = original_tree.getroot()

        # Load the current root node from thesis_tree_6_i.xml
        tree_i = ET.parse(tree_path_format.format(i=j))
        root_i = tree_i.getroot()
        root_node_i = root_i.find("node")

        # Find all nodes in thesis_tree_large.xml that have exactly one <label> child
        candidate_nodes = []
        for node in original_root.iter("node"):
            if (
                len(list(node)) == 1
                and node.find("label") is not None
                and "switchRole" not in node.attrib
            ):
                candidate_nodes.append(node)

        # Choose a random node from the candidates
        if not candidate_nodes:
            raise ValueError("No valid node found to replace")
        random_node_to_replace = random.choice(candidate_nodes)

        # Replace the randomly chosen node in thesis_tree_large.xml with the root node from thesis_tree_6_i.xml
        random_node_to_replace.clear()
        random_node_to_replace.tag = root_node_i.tag
        random_node_to_replace.attrib = root_node_i.attrib
        random_node_to_replace.extend(root_node_i)

        # Save the modified XML to a new file
        ET.indent(original_tree, space="  ", level=0)
        original_tree.write(tree_path)
        os.remove(tree_path_format.format(i=j))


filePath = "./util/thesis_tree.xml"
formatFile = filePath[:-4] + "_{i}" + ".xml"

for i in range(8):
    modify_labels(filePath, formatFile.format(i=i))

merge_trees(filePath, formatFile)
