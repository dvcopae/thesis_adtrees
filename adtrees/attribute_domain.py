from itertools import chain, combinations, product

from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment
from colorama import Fore, init

from util.util import remove_dominated_pts, remove_low_att_pts

init(autoreset=True)

PRINT_INTERMEDIATE = False
MAX_PARETO_SIZE = 0


def powerset(iterable):
    """powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


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
        """Exponential in the number of basic events."""
        pts = []
        all_defenses = T.get_basic_actions("d")
        all_attacks = T.get_basic_actions("a")

        for active_defs in powerset(all_defenses):
            pts_candidates = []
            def_cost = sum([ba[d] for d in all_defenses if d in active_defs])

            for active_atts in powerset(all_attacks):
                new_assignment = BasicAssignment()

                for a in all_attacks:
                    new_assignment[a] = ba[a] if a in active_atts else self.absorb_a

                for d in all_defenses:
                    new_assignment[d] = ba[d] if d in active_defs else self.neutral_d

                activation_map = self.get_activation_map(T, new_assignment)

                if T.is_strategy_successful(activation_map):  # successful
                    att_cost = sum([ba[a] for a in all_attacks if a in active_atts])

                    pts_candidates.append((def_cost, att_cost))

            reduced_candidates = (
                [(def_cost, float("inf"))]
                if len(pts_candidates) == 0
                else remove_dominated_pts(T.root.type, pts_candidates)
            )

            if print_progress:
                print(f"Added for defense {active_defs} : {reduced_candidates}")

            pts.extend(reduced_candidates)

        pts = remove_low_att_pts(T.root.type, pts)
        pts = remove_dominated_pts(T.root.type, pts)

        print(pts)

        return pts

    def evaluate_dummy_bu(self, T: ADTree, ba: BasicAssignment, print_progress: True):
        """Exponential in the number of basic defense steps."""
        pts = []
        all_defenses = T.get_basic_actions("d")
        all_attacks = T.get_basic_actions("a")

        for active_defs in powerset(all_defenses):
            new_assignment = BasicAssignment()
            for a in all_attacks:
                new_assignment[a] = ba[a]

            # When a defense activate, equate its cost with the neutral element
            for d in all_defenses:
                new_assignment[d] = ba[d] if d in active_defs else self.neutral_d

            bu_result = self.__bottomup(T, T.root, new_assignment)

            if print_progress:
                print(f"Added for defense {active_defs} : {bu_result}")
            pts.extend(bu_result)

        pf = remove_dominated_pts(T.root.type, pts)

        if not T.is_proper_tree():
            print(
                Fore.YELLOW
                + "## WARNING ##: The results are not correct since the tree is a DAG."
            )

        print(pf)
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
            raise ValueError(
                f"Cannot perform the attribute evaluation: Actions {missing} have no value assigned."
            )

        PRINT_INTERMEDIATE = print_progress

        bu = self.__bottomup(T, T.root, ba)

        if print_progress:
            print(f"Pareto Front Size: {len(bu)}")
            print(f"Max P.F. Size: {MAX_PARETO_SIZE}")
            if not T.is_proper_tree():
                print(
                    Fore.YELLOW
                    + "## WARNING ##: The results are not correct since the tree is a DAG."
                )
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
        elif node.ref == "":  # Basic action
            pts = (
                [(0, float(ba[node.label]))]
                if node.type == "a"
                else [(0, 0), (ba[node.label], float("inf"))]
            )
        else:  # AND / OR nodes
            pts = self._process_children(T, node, ba)

        pf = remove_dominated_pts(node.type, pts)

        if PRINT_INTERMEDIATE:
            color = Fore.RED if node.type == "a" else Fore.GREEN
            print(
                color
                + f"{'(INH) ' if is_inh_gate else ''}{node}, (Size {len(pf)}), {pf}"
            )
            MAX_PARETO_SIZE = max(MAX_PARETO_SIZE, len(pf))

        return pf

    def _get_combine_operators(self, actor, node_ref):
        if node_ref == "AND" or node_ref == "INH":
            return (self.and_d, self.and_a) if actor == "a" else (self.and_d, self.or_a)
        else:
            return (self.and_d, self.or_a) if actor == "a" else (self.and_d, self.and_a)

    def _process_children(self, T: ADTree, node: ADNode, ba: BasicAssignment):
        pf_map = {}

        for child in T.get_children(node):
            if T.get_counter(node) != child:
                pf_map[child.label] = self.__bottomup(T, child, ba)

        strategies = []
        def_op, att_op = self._get_combine_operators(node.type, node.ref)

        for cart_prod in product(*list(pf_map.values())):
            strategies.append(
                (def_op([p[0] for p in cart_prod]), att_op([p[1] for p in cart_prod]))
            )

        return remove_dominated_pts(node.type, strategies)

    def _bottom_up_inh(
        self, T: ADTree, action: ADNode, counter: ADNode, ba: BasicAssignment
    ):
        action_pf = self.__bottomup(T, action, ba, check_countered=False)
        counter_pf = self.__bottomup(T, counter, ba)

        def_op, att_op = self._get_combine_operators(action.type, "INH")

        strategies = [
            (def_op([act_def, cnt_def]), att_op([act_att, cnt_att]))
            for act_def, act_att in action_pf
            for cnt_def, cnt_att in counter_pf
        ]

        return remove_dominated_pts(action.type, strategies)

    def get_activation_map(self, T: ADTree, ba: BasicAssignment):
        activations = {}
        for d in T.get_basic_actions("d"):
            activations[d] = False if ba[d] == self.neutral_d else True

        for a in T.get_basic_actions("a"):
            activations[a] = False if ba[a] == self.absorb_a else True

        return activations
