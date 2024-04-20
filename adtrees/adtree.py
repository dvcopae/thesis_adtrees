from adtrees.adnode import ADNode
from util.adtparser import file_to_dict
from copy import deepcopy


class ADTree:
    """
    Implementation of attack-defense trees.

    class ADTree(self, path, dictionary, attack_tree)

    Parameters
    ----------
    path: str, default ''
        Path to an .xml output file produced by ADTool. If provided, the tree is loaded from the file.
    dictionary : dict, empty by default
        Dictionary with keys being ADNodes and values being lists
        of ADNodes. Dictionary[node] is a list of children of the node.

    Examples
    ----------
    >>> x = ADNode('a', 'break in', 'OR')
    >>> x1 = ADNode('a', 'break in through the back door')
    >>> x2 = ADNode('a', 'break in through one of the windows')
    >>> y1 = ADNode('d', 'install lock on the back door')
    >>> d = {x: [x1, x2], x1: [y1], x2: [], y1: []}
    >>> T1 = ADTree(dictionary=d)
    >>> T1.output('tree.xml')
    >>> T2 = ADTree('tree.xml')
    """

    def __init__(self, path='', dictionary=None):
        """
        self.ad_term
        self.attack
        self.basics
        self.dict
        self.root
        """
        super(ADTree, self).__init__()

        if dictionary is None:
            dictionary = {}

        # creating dictionary from ADTool's .xml file
        if isinstance(path, str) and path[-4:] == '.xml':
            self.dict = file_to_dict(path)
            if self.dict is None:
                return
            # set root
            nodes_having_parents = []
            for key in self.dict:
                for node in self.dict[key]:
                    nodes_having_parents.append(node)
            # set root
            for node in self.dict:
                if node not in nodes_having_parents:
                    self.root = node
                    break

        # creating dictionary from a dictionary
        elif isinstance(dictionary, dict) and len(dictionary) > 0:
            # tree is created from a dictionary.
            # check if the dictionary actually describes a tree
            keys = [i for i in dictionary.keys()]
            in_lists = [node for item in dictionary.values()
                        for node in item]
            # 1. every element that is in one of the lists is also a key of the dictionary; and it is an ADNode
            for item in in_lists:
                if not isinstance(item, ADNode) or item not in keys:
                    print(
                        'Either dictionary does not describe a tree or else not all of the elements are ADNodes.')
                    help(ADTree)
                    return
            # 2. there is exactly one element in the keys that is not in the lists, namely, the root of the tree.
            roots = [i for i in keys if i not in set(in_lists)]
            if len(roots) != 1:
                print('Invalid number of roots.')
                help(ADTree)
                return
            elif not isinstance(roots[0], ADNode):
                print('At least one of the dictionary keys is not an ADNode.')
                help(ADTree)
                return
            self.root = roots[0]
            # finally, create self.dict.
            self.dict = {}
            for key in keys:
                self.dict[key] = dictionary[key]
        else:
            self.attack = True
            self.root = ADNode(label='root')
            self.dict = {self.root: []}
        # set term
        self.ad_term = self.ad_term()
        # store the set of all nodes holding basic actions of the tree.
        self.basics = set(
            [node for node in self.dict.keys() if node.is_basic()])

    def ad_term(self, node=None):
        """
        Given an ADTree T and one of its nodes, create an ADTerm that corresponds
        to the subtree of T rooted in the node.
        If no node passed, then the ADTerm created corresponds to T.
        """
        if node is None:
            node = self.root
        countered = self.is_countered(node)
        countermeasure = self.get_counter(node)
        if node.is_basic():
            # the node represents a basic action; has at most one child,
            # which is a countermeasure
            if not countered:
                # the node is a leaf of the tree
                return node.label
            else:
                return 'C' + node.type + '(' + node.label + ',' + self.ad_term(countermeasure) + ')'
        else:
            # else the node is refined and has children of the same type.
            if countered:
                result = 'C' + node.type + '(' + node.ref + node.type + '('
                for child in self.dict[node]:
                    if child != countermeasure:
                        result += self.ad_term(child)
                        result += ','
                # put the countermeasure at the end
                result = result[:-1] + '),'
                result += self.ad_term(countermeasure)
                result += ')'
                return result
            else:
                result = node.ref + node.type + '('
                for child in self.dict[node]:
                    result += self.ad_term(child)
                    result += ','
                result = result[:-1] + ')'
                return result

    def get_basic_actions(self, actor=None):
        """
        Return the list of labels of basic actions of a given actor ('a', 'd' or None) in the tree.
        If no actor provided, return the list of all basic actions.
        """
        if actor not in ['a', 'd', None]:
            help(ADTree)
            return
        bas = []
        if actor is None:
            allowed = ['a', 'd']
        else:
            allowed = [actor]
        for node in self.basics:
            if node.type in allowed:
                if node.label not in bas:
                    bas.append(node.label)
        return bas

    def get_children(self, node):
        """
        Return list of the children of a node (including countermeasure).
        """
        return self.dict[node]

    def subtree_size(self):
        children = 0

        new_tree = deepcopy(self)

        unvisited = new_tree.get_children(new_tree.root)
        while unvisited:
            current = unvisited.pop(0)
            children += 1
            unvisited.extend(new_tree.get_children(current))

        return children

    def is_countered(self, node):
        if self.get_counter(node) is not None:
            return True
        return False

    def get_counter(self, node):
        """
        Return a countermeasure to a given node, if there is one.
        False otherwise.

        Returns ADNode.
        """
        if node not in self.dict:
            print('Node provided does not belong to the tree.')
            print()
            help(ADTree.get_counter)
            return
        ntype = node.type
        for child in self.dict[node]:
            if child.type != ntype:
                return child
        return None

    def get_parent(self, node):
        """
        Return parent node of a given node.
        """
        for candidate, children in self.dict.items():
            if node in children:
                return candidate
        return None

    def is_proper_tree(self):
        if self.root.type == 'a':
            # attacker is the proponent
            a_role = 'p'
            d_role = 'o'
        else:
            a_role = 'o'
            d_role = 'p'
        for b in self.get_basic_actions('a'):
            if self.is_duplicated_label(b, a_role):
                return False
        for b in self.get_basic_actions('d'):
            if self.is_duplicated_label(b, d_role):
                return False
        return True

    def is_duplicated_label(self, label, actor='p'):
        """
        Return True iff there are more than one
        node (of the specified actor: proponent or opponent)
        holding a basic action that bear the same label 'label'.
        """
        if actor == 'p':
            actor = self.root.type
        else:
            if self.root.type == 'a':
                actor = 'd'
            else:
                actor = 'a'

        all_basic_labels = self.get_basic_actions(actor)
        if label not in all_basic_labels:
            return False
        counter = 0
        for node in self.basics:
            if node.type == actor and node.label == label:
                counter += 1
            if counter > 1:
                return True
        return False

    def order(self):
        """
        return the number of nodes in self.
        """
        return len(self.dict)

    def __xml__(self, node=None, counter=0):
        """
        Create contents of the output file created by output().
        Keep only the structure and labels of nodes holding basic actions.

        //Node treated as a countermeasure if counter = 1; technical parameter.
        """
        if node is None:
            node = self.root
        countered = self.is_countered(node)
        countermeasure = self.get_counter(node)

        if node.ref == 'AND':
            ref = '"conjunctive"'
        else:
            # in ADTool 2.2.2, default refinement for basic actions is
            # "disjunctive"
            ref = '"disjunctive"'

        if not counter:
            # if the node is not a countermeasure itself, no switching of
            # actors
            prefix = '\t<node refinement=' + ref + '>\n' + \
                     '\t\t<label>' + node.label + '</label>\n\t'
        else:
            # if the node itself is a countermeasure, switch actors
            prefix = '\t<node refinement=' + ref + ' switchRole="yes">\n' + \
                     '\t\t<label>' + node.label + '</label>\n\t'

        result = prefix
        for child in self.dict[node]:
            if child != countermeasure:
                result += self.__xml__(child)
        if countered:
            result += self.__xml__(countermeasure, 1)
        result += '</node>\n'
        return result

    def output(self, name=''):
        """
        Create an .xml file corresponding to self that will be accepted as input by ADTool.
        """
        if name == '':
            print('Provide a name for the output file.')
            return
        if name[-4:] != '.xml':
            name += '.xml'
        with open(name, 'w') as f:
            f.write("<?xml version='1.0'?>\n")
            f.write('<adtree>\n')
            f.write(self.__xml__(self.root))
            f.write('</adtree>')
        print('Tree structure written to "' +
              name + '", ready to be opened with ADTool!')
        return

    def __repr__(self):
        return self.ad_term
