import os.path
import xml.etree.ElementTree as ET
import secrets
import string


def generate_random_string(length=10):
    # Generate a random string of fixed length
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def modify_labels(xml_path, output_path):
    # Load the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Modify each label element
    labels = root.findall('.//label')
    for label in labels:
        random_string = generate_random_string()
        label.text = random_string

    # Write the modified XML to a new file
    tree.write(output_path)


input_xml_path = os.path.join('../trees', 'rfid_large_80.xml')
for i in range(10):
    modify_labels(input_xml_path, os.path.join('../trees', f'rfid_large_{i}.xml'))

