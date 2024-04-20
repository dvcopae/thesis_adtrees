from itertools import chain, combinations, product

from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment
from colorama import Fore, init

init(autoreset=True)

PRINT_INTERMEDIATE = False
MAX_PARETO_SIZE = 0


def powerset(iterable):
    """powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def _reduce_pf_points(actor, points):
    if not points:
        return []

    actor_index = 0 if actor == 'd' else 1
    sorted_points = sorted(points, key=lambda e: (e[actor_index], e[1 - actor_index]))

    pareto_front = [sorted_points[0]]
    for point in sorted_points[1:]:
        if point[0] > pareto_front[-1][0] and point[1] > pareto_front[-1][1]:
            pareto_front.append(point)

    return pareto_front


class AttrDomain:
    """
    Implementation of an attribute domain for AND-OR-C attack-defense trees.

    class AttrDomain(self, orp, andp, oro, ando, cp, co)

    Parameters
    ----------
    or_d, and_d : binary functions defined for the same type of arguments.
                Operations to be performed at ORp, ANDp

    or_a, and_a : binary functions defined for the same type of arguments, default None.
             Operations to be performed at ORo, ANDo, Cp, Cp nodes, respectively.

    If only orp and andp provided, it is assummed that the domain satisfies
    orp = ando = co,
    andp = oro = cp.

    Examples
    ----------
    >>> root = ADNode('a', 'root', 'AND')
    >>> child1 = ADNode('a', label='a')
    >>> child2 = ADNode('a', label = 'b')
    >>> T = ADTree(dictionary = {root: [child1, child2], child1: [], child2: []})
    >>> minCostofAttack = AttrDomain(min, lambda x, y: x + y)
    >>> ba = BasicAssignment()
    >>> ba['a'] = 10
    >>> ba['b'] = 5
    >>> minCostofAttack.evaluate_bu(T, ba)
    15
    """

    def __init__(self, or_d, and_d, or_a, and_a, neutral_d, absorb_a):
        self.or_d = or_d
        self.and_d = and_d
        self.neutral_d = neutral_d
        self.absorb_a = absorb_a
        if None in [or_a, and_a]:
            self.or_a = and_d
            self.and_a = or_d
        else:
            self.or_a = or_a
            self.and_a = and_a

    def evaluate_dummiest(self, T: ADTree, ba: BasicAssignment, print_progress: True):
        """ Exponential in the number of basic events. """
        pts = []
        all_defenses = T.get_basic_actions('d')
        all_attacks = T.get_basic_actions('a')

        for active_defs, active_atts in product(powerset(all_defenses), powerset(all_attacks)):
            new_assignment = BasicAssignment()

            for a in all_attacks:
                new_assignment[a] = ba[a] if a in active_atts else self.absorb_a

            for d in all_defenses:
                new_assignment[d] = ba[d] if d in active_defs else self.neutral_d

            bu_result = self.__bottomup(T, T.root, new_assignment)
            if bu_result != [(0, float('inf'))]:  # successful
                def_cost = sum([ba[d] for d in all_defenses if d in active_defs])
                att_cost = sum([ba[a] for a in all_attacks if a in active_atts])
                pts.append((def_cost, att_cost))

        pf = _reduce_pf_points(T.root.ref, pts)

        if print_progress:
            print(f'(Size {len(pf)})' + str(pf))
            print()

        return pf

    def evaluate_dummy_bu(self, T: ADTree, ba: BasicAssignment, print_progress: True):
        """ Exponential in the number of basic defense steps. """
        pts = []
        all_defenses = T.get_basic_actions('d')
        all_attacks = T.get_basic_actions('a')

        for active_defs in powerset(all_defenses):
            new_assignment = BasicAssignment()
            for a in all_attacks:
                new_assignment[a] = ba[a]

            # When a defense activate, equate its cost with the neutral element
            for d in all_defenses:
                new_assignment[d] = ba[d] if d in active_defs else self.neutral_d

            pts.extend(self.__bottomup(T, T.root, new_assignment))

        pf = _reduce_pf_points(T.root.ref, pts)

        if print_progress:
            print(f'(Size {len(pf)})' + str(pf))
            if not T.is_proper_tree():
                print(Fore.YELLOW + "## WARNING ##: The results are not correct since the tree is a DAG.")

        return pf

    def evaluate_bu(self, T: ADTree, ba: BasicAssignment, print_progress: True):
        """
        Compute the value of the attribute modeled with the 'self' domain
        in the tree 'T', under the basic assignment 'ba', using
        the bottom-up evaluation.
        """
        global PRINT_INTERMEDIATE

        # if not T.is_proper_tree():
        #     raise TypeError('T is not a proper tree')

        # initial checks; make sure that every basic action is assigned a value
        if missing := [label for label in T.get_basic_actions() if label not in ba]:
            raise ValueError(f'Cannot perform the attribute evaluation: Actions {missing} have no value assigned.')

        PRINT_INTERMEDIATE = print_progress

        bu = self.__bottomup(T, T.root, ba)

        if print_progress:
            print(f'Pareto Front Size: {len(bu)}')
            print(f'Max P.F. Size: {MAX_PARETO_SIZE}')
            if not T.is_proper_tree():
                print(Fore.YELLOW + "## WARNING ##: The results are not correct since the tree is a DAG.")
        return bu

    def __bottomup(self, T, node: ADNode, ba: BasicAssignment, check_countered=True):
        """
        Value of the attribute obtained at 'node' of adtree 'T' when using the
        bottom-up procedure under the basic assignment 'ba'.

        proponent in {'a', 'd'}.
        """

        global MAX_PARETO_SIZE

        is_inh_gate = check_countered and T.is_countered(node)

        if is_inh_gate:
            counter_node = T.get_counter(node)
            # we have an INH gate between `node` and `counter_node`
            pts = self._bottom_up_inh(T, node, counter_node, ba)
        elif node.ref == '':  # Basic action
            pts = [(0, float(ba[node.label]))] if node.type == 'a' \
                else [(0, 0), (ba[node.label], float('inf'))]
        else:  # AND / OR nodes
            pts = self._process_children(T, node, ba)

        pf = _reduce_pf_points(node.ref, pts)

        if PRINT_INTERMEDIATE:
            color = Fore.RED if node.type == 'a' else Fore.GREEN
            print(color + f"{'(INH) ' if is_inh_gate else ''}{node}, (Size {len(pf)}), {pf}")
            MAX_PARETO_SIZE = max(MAX_PARETO_SIZE, len(pf))

        return pf

    def _get_combine_operators(self, actor, node_ref):
        if node_ref == 'AND' or node_ref == 'INH':
            return (self.and_d, self.and_a) if actor == 'a' else (self.and_d, self.or_a)
        else:
            return (self.and_d, self.or_a) if actor == 'a' else (self.and_d, self.and_a)

    def _process_children(self, T: ADTree, node: ADNode, ba: BasicAssignment):
        pf_map = {}

        for child in T.get_children(node):
            if T.get_counter(node) != child:
                pf_map[child.label] = self.__bottomup(T, child, ba)

        strategies = []
        def_op, att_op = self._get_combine_operators(node.type, node.ref)

        for cart_prod in product(*list(pf_map.values())):
            strategies.append((def_op([p[0] for p in cart_prod]), att_op([p[1] for p in cart_prod])))

        return _reduce_pf_points(node.type, strategies)

    def _bottom_up_inh(self, T: ADTree, action: ADNode, counter: ADNode, ba: BasicAssignment):
        action_pf = self.__bottomup(T, action, ba, check_countered=False)
        counter_pf = self.__bottomup(T, counter, ba)

        def_op, att_op = self._get_combine_operators(action.type, 'INH')

        strategies = [(def_op([act_def, cnt_def]), att_op([act_att, cnt_att])) for act_def, act_att in action_pf
                      for cnt_def, cnt_att in counter_pf]

        return _reduce_pf_points(action.type, strategies)
