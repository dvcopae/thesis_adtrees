from copy import deepcopy

from utils.adtparser import get_basic_assignment_xml
from utils.util import clean_tla_identifier


def _from_xml(path):
    return get_basic_assignment_xml(path)


def _from_txt(path):
    """
    Initialize the basic assignment for a .txt file formatted as follows:

    label1\tvalue1
    label2\tvalue2
    ...
    labelk\tvaluek

    Note that between 'labeli' and 'valuei' there is an indent.

    Such a file can be created using self.output(filename).

    Lines beginning with '#' are ignored (comment lines).
    """
    result = {}
    try:
        with open(path, "rt") as f:
            line = f.readline()  # = 'label\tvalue\n'
            while line != "" and line[0] == "#":
                line = f.readline()
            # the behaviour depends on whether the 'value' is a list (for Pareto domain) # or not
            if "[" in line:
                # we are dealing with the Pareto basic assignment.
                # the lines are of the form 'label\t[[v1, v2, ..., vk]]\n'
                while line != "":
                    line_content = line.strip().split("\t")
                    label = clean_tla_identifier(line_content[0])
                    values = line_content[1][2:-2].split(", ")
                    value = [[float(i) for i in values]]
                    result[label] = value
                    # done, move to the next line.
                    line = f.readline()
                    while line != "" and line[0] == "#":
                        line = f.readline()
            else:
                # the lines are of the form 'label\tvalue\n'
                while line != "":
                    line_content = line.strip().split("\t")
                    label = clean_tla_identifier(line_content[0])
                    value = float(line_content[1])
                    result[label] = value
                    # done, move to the next line.
                    line = f.readline()
                    while line != "" and line[0] == "#":
                        line = f.readline()
    except FileNotFoundError:
        print(
            "Couldn't load basic assignment from {}\n There is no such file or directory.".format(
                path
            )
        )
    return result


class BasicAssignment:
    """
    Representation of a basic assignment of an attribute.

    class BasicAssignment(self, path)

    Parameters
    ----------
    path : string, default ''
        Path to
            ADTool's output .xml file storing a tree with a basic assignment.
        or
            a .txt file storing a basic assignment.

    If no path provided, an empty basic assignment is created, ready to be populated.
    """

    def __init__(self, path=None):
        super(BasicAssignment, self).__init__()

        if isinstance(path, str):
            if path[-4:] == ".xml":
                # initialize from ADTool's .xml file
                self.map = _from_xml(path)
            elif path[-4:] == ".txt":
                # initialize from a .txt file
                self.map = _from_txt(path)
        else:
            # initialize with an empty dictionary
            self.map = {}

    def deepcopy(self):
        new = BasicAssignment()
        new.map = deepcopy(self.map)
        return new

    def __contains__(self, label):
        """
        Check whether 'label' is assigned a value under the assignment 'self'.
        """
        return label in self.map

    def __iter__(self):
        for item in self.map:
            yield item

    def __setitem__(self, label, value):
        """
        Update or add a value corresponding to an action.
        """
        self.map[str(label)] = value

    def __getitem__(self, label):
        if str(label) in self:
            return self.map[str(label)]
        else:
            raise ValueError(
                "The action '" + str(label) + "' is not assigned any value."
            )

    def output(self, name):
        """
        Creates a file named 'name.txt' containing the basic assignment.
        The file is formatted as

        label1\tvalue1\n
        label2\tvalue2\n
        ...
        labelk\tvaluek\n
        """
        if isinstance(name, str):
            name = str(name)
        else:
            print("The name should be a string, or convertible to string.")
            return

        if name[-4:] != ".txt":
            name += ".txt"

        with open(name, "w") as f:
            for label in self:
                out_label = str(label).replace("\n", " ")
                f.write(out_label + "\t" + str(self[label]) + "\n")
        return

    def __eq__(self, other):
        return self.map == other.map

    def __repr__(self):
        res = ""
        for label in self.map:
            res += str(label) + "\t" + str(self.map[label]) + "\n"
        return res
