import os
import sys
import xml.etree.ElementTree as ET
import random
import numpy as np
from pathlib import Path


# Function to check if node meets the conditions
def needs_parameter(node):
    return (len(node) == 1 and node[0].tag == 'label') or (len(node) <= 3 and 'switchRole' in node[1].attrib)


def add_values_to_basic_events(file_path):
    # Load the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Traverse all 'node' elements and modify as needed
    for node in root.iter('node'):
        if needs_parameter(node):
            # Create a new 'parameter' element
            parameter = ET.Element('parameter')
            parameter.set('domainId', 'MinCost1')
            parameter.set('category', 'basic')
            parameter.text = str(random.randint(1, int(1e5)))

            # Add the new element to the 'node', directly after the 'label' child
            node.insert(1, parameter)

    # Save the modified tree to a new file
    domain = ET.Element('domain')
    domain.set('id', 'MinCost1')
    clazz = ET.Element('class')
    clazz.text = 'lu.uni.adtool.domains.adtpredefined.MinCost'
    tool = ET.Element('tool')
    tool.text = 'ADTool2'
    domain.append(clazz)
    domain.append(tool)

    root.append(domain)

    ET.indent(tree, space="  ", level=0)
    tree.write(os.path.join('../trees_w_assignments', Path(file_path).stem + '_modified.xml'))


add_values_to_basic_events(os.path.join('rfid_reduced.xml'))
