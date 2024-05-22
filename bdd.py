import itertools
import os
import re
from timeit import default_timer as timer
from typing import List, Tuple

import dd.bdd as _bdd
from colorama import Fore, init

from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment
from utils.util import remove_dominated_pts, remove_high_def_pts, remove_low_att_pts

init(autoreset=True)


def _eval_path_cost(
    path: dict, ba: BasicAssignment, defenses: List[str], attacks: List[str]
) -> Tuple[float, float]:
    def_cost = sum([ba[d] for d in defenses if d in path and path[d]])
    att_cost = sum([ba[a] for a in attacks if a in path and path[a]])
    return (def_cost, att_cost)


pf_storage = {}


def find_pareto_bu(
    bdd: _bdd.BDD,
    u,
    defenses: List[str],
    ba: BasicAssignment,
    goal=True,
):
    # Avoid revisiting nodes
    if u in pf_storage:
        return pf_storage[u]

    p = abs(u)

    # Complemented edge, swap goal
    if u < 0:
        goal = not goal

    # terminal ?
    if p == 1:
        return [(0, 0)] if goal else [(0, float("inf"))]

    # non-terminal
    i, v, w = bdd._succ[p]
    if not v:
        raise AssertionError(v)
    if not w:
        raise AssertionError(w)

    pf_left = find_pareto_bu(bdd, v, defenses, ba, goal)
    pf_right = find_pareto_bu(bdd, w, defenses, ba, goal)

    # Taking a `right` edge means we activated `u`, so add it's cost
    u_label = bdd._level_to_var[i]
    is_defense = u_label in defenses

    if is_defense:
        pf_right = [(d + ba[u_label], a) for d, a in pf_right]
    else:
        pf_right = [(d, a + ba[u_label]) for d, a in pf_right]

    pf = pf_left + pf_right

    if is_defense:
        pf = remove_low_att_pts(pf)

    pf = remove_dominated_pts("a", pf)

    pf_storage[u] = pf

    return pf


def find_paths_bdd(bdd: _bdd.BDD, u, path={}, goal=True):
    """Recurse to enumerate models."""

    p = abs(u)

    # Complemented edge, swap goal
    if u < 0:
        goal = not goal

    # terminal ?
    if p == 1:
        if goal:
            yield {bdd._level_to_var[i]: v for i, v in path.items()}
        return

    # non-terminal
    i, v, w = bdd._succ[p]
    if not v:
        raise AssertionError(v)
    if not w:
        raise AssertionError(w)

    path_u_false = dict(path)
    path_u_false[i] = False

    path_u_true = dict(path)
    path_u_true[i] = True

    for x in find_paths_bdd(bdd, v, path_u_false, goal):
        yield x
    for x in find_paths_bdd(bdd, w, path_u_true, goal):
        yield x


def compute_pf_all_paths(
    bdd: _bdd.BDD,
    root: ADNode,
    ba: BasicAssignment,
    defenses: List[str],
    attacks: List[str],
) -> List[float]:
    pf_dict = {}
    all_paths = []
    defense_vecs_passed = set()

    for c in find_paths_bdd(bdd, root):
        def_cost, att_cost = _eval_path_cost(c, ba, defenses, attacks)

        # Fill path with missing defenses, and keep track of which defense configurations we encountered
        # def_in_path = tuple()
        for d in defenses:
            if d not in c:
                c[d] = False
            # elif c[d]:
            #    def_in_path = def_in_path + (d, ) 
        
        # Fill path with missing attacks
        for a in attacks:
            if a not in c:
                c[a] = False

        all_paths.append(c)
        # defense_vecs_passed.add(def_in_path)

        prev_path = pf_dict.get(def_cost)
        if prev_path:
            _, prev_att_cost = _eval_path_cost(prev_path, ba, defenses, attacks)
            if all(prev_path[d] == c[d] for d in defenses):
                if att_cost < prev_att_cost:
                    # We have the same defense vector as the current solution -> MINIMIZE att_cost
                    pf_dict[def_cost] = c
            else:
                # We found another defense vector which has the same def_cost -> MAXIMIZE att_cost
                if att_cost > prev_att_cost:
                    pf_dict[def_cost] = c
        else:
            # Value not in dict, add it
            pf_dict[def_cost] = c

        if PRINT_PROGRESS:
            print(Fore.GREEN + f"{(def_cost, att_cost)} {c}")

    pf_dict_paths = pf_dict.values()

    pf = [_eval_path_cost(c, ba, defenses, attacks) for c in pf_dict_paths]

    # Add infty costs - EXPENSIVE
    # infinities = []
    # for def_vector in itertools.product([False, True], repeat=len(defenses)):
    #     def_dict = dict(zip(defenses, def_vector))
    #     vector_defs = tuple([k for k,v in def_dict.items() if k in defenses and v])
        
    #     # Check if `def_dict` is not found as a solution
    #     if not any(
    #         all(path[key] == value for key, value in def_dict.items())
    #         for path in all_paths
    #     ):
    #         def_cost = sum([ba[defense] for defense in vector_defs])
    #         if PRINT_PROGRESS:
    #             print(Fore.YELLOW + f"{(def_cost, float("inf"))} {def_dict}")
    #         infinities.append((def_cost, float("inf")))

    # # We are only interested in the minimum defense cost which produces infinity            
    # pf.extend(remove_high_def_pts(infinities))
    
    # print(f"ini: {pf}")
    print(f"def: {remove_dominated_pts("d", pf)}")
    print(f"att: {remove_dominated_pts("a", pf)}")

    pf = remove_low_att_pts(pf)
    pf = remove_dominated_pts("d", pf)

    return pf


def extract_order(formula, variables):
    order = []
    for var in variables:
        match = re.search(r"\b" + re.escape(var) + r"\b", formula)
        if match:
            order.append((match.start(), var))
    order.sort()
    return [var for _, var in order]


def create_mapping(formula, defenses, attacks):
    # Extract the order of appearance for defenses and attacks
    defense_order = extract_order(formula, defenses)
    attack_order = extract_order(formula, attacks)

    # Create the dictionary with defenses first, followed by attacks
    mapping = {}
    index = 0

    for defense in defense_order + [d for d in defenses if d not in defense_order]:
        mapping[defense] = index
        index += 1

    for attack in attack_order + [a for a in attacks if a not in attack_order]:
        mapping[attack] = index
        index += 1

    return mapping


def run(filepath, method="bu", dump=False):
    # reset pf_Storage for bdd_bu
    global pf_storage
    pf_storage = {}

    ba = BasicAssignment(filepath)
    T = ADTree(filepath)
    defenses = T.get_basic_actions("d")
    attacks = T.get_basic_actions("a")

    start = timer()

    bdd = _bdd.BDD()
    bdd.configure(reordering=False)
    bdd.declare(*(defenses + attacks))
    expr = T.get_boolean_expression()
    TREE = bdd.add_expr(expr)
    # custom_order = create_mapping(expr, defenses, attacks)
    custom_order = {d: i for i, d in enumerate(defenses + attacks)}
    print(custom_order)

    if PRINT_PROGRESS:
        print(f"Initial size: {len(bdd)}")

    _bdd.reorder(bdd, custom_order)

    if dump:
        bdd.dump("./bdds/bdd_graph_custom_reorder.png", roots=[TREE])

    if PRINT_PROGRESS:
        print(f"Size after custom-order: {len(bdd)}")

    if method == "bu":
        pf = find_pareto_bu(bdd, TREE, defenses, ba)
    elif method == "all_paths":
        pf = compute_pf_all_paths(bdd, TREE, ba, defenses, attacks)

    time = timer() - start

    return time, pf


PRINT_PROGRESS = False


def run_average(filepath, NO_RUNS=100, method="bu"):
    return sum(run(filepath, method)[0] for _ in range(0, NO_RUNS)) / NO_RUNS


if __name__ == "__main__":
    print("===== BDD =====\n")
    # for i in [6, 12, 18, 24, 30, 36, 42, 48, 54]:
    #     filepath = f"./data/trees_w_assignments/tree_{i}.xml"
    #     print(os.path.basename(filepath))

    #     # Average time over `NO_RUNS`, excluding the time to read the tree
    #     time = run_average(filepath, NO_RUNS=1, method="bu")
    #     _, pf = run(filepath)
    #     print(pf)

    #     print("Time: {:.2f} ms.\n".format(time * 1000))

    time, pf = run(
        "./data/trees_w_assignments/tree_54.xml",
        method="all_paths",
        dump=False,
    )
    print(pf)
    print("Time: {:.2f} ms.\n".format(time * 1000))
