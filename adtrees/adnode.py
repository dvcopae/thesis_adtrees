from __future__ import annotations


class ADNode:
    """
    Representation of a node of an attack-defense tree. Building block for
    objects of the ADTree class.

    class ADNode(self, actor, label, refinement)

    Parameters
    ----------
    actor : {'a', 'd'}, default 'a'
        Value describing which actor's goal/basic action the node represents.
        'a' for a node of the attacker, 'd' for a node of the defender.
    label : string, default 'NoName'
        Name of a goal/basic action the node represents.
    refinement : {'AND', 'OR', None}, default None
        'AND' for a conjunctively refined node, 'OR' for a disjunctively refined
        node, None for a basic action.

    Examples
    ----------
    >>> x = ADNode('a', 'break in', 'OR')
    >>> x1 = ADNode('a', 'break in through the back door')
    >>> x2 = ADNode('a', 'break in through one of the windows')
    >>> y1 = ADNode('d', 'install lock on the back door')
    """

    def __init__(self, actor="a", label="NoName", refinement=None):
        """
        initialize self.

        type, label, ref

        """
        super().__init__()
        # check whether the parameters provided are OK.
        # actor
        if actor not in ["a", "d"]:
            print(f"Invalid actor: {actor}")
            help(ADNode)
            return
        self.type = actor
        # label
        try:
            self.label = str(label)
        except:
            print("Invalid label.")
            help(ADNode)
            return

        # refinement
        if refinement in ["AND", "OR"]:
            self.ref = refinement
        elif refinement is None:
            self.ref = ""
        else:
            print(f"Invalid refinement: {refinement}")
            help(ADNode)
            return

    def copy(self):
        """
        Return a copy of the node.
        """
        return ADNode(self.type, self.label, self.ref)

    def is_basic(self):
        """
        True iff the node represents a basic action, i.e., if it is not
        refined.
        """
        return self.ref == ""

    def __repr__(self):
        if self.is_basic():
            return f"({self.type}, {self.label}, {'BS'})"
        return f"({self.type}, {self.label}, {self.ref})"
