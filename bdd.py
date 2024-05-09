import itertools
from typing import List, Tuple
import dd.bdd as _bdd

from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment

from colorama import Fore, init

from timeit import default_timer as timer

from util.util import remove_dominated_pts

init(autoreset=True)


def _eval_path_cost(
    path: dict, ba: BasicAssignment, defenses: List[str], attacks: List[str]
) -> Tuple[float, float]:
    def_cost = sum([ba[d] for d in defenses if d in path and path[d]])
    att_cost = sum([ba[a] for a in attacks if a in path and path[a]])
    return (def_cost, att_cost)


def compute_pf(
    bdd: _bdd.BDD,
    root: ADNode,
    ba: BasicAssignment,
    defenses: List[str],
    attacks: List[str],
) -> List[float]:
    pf_dict = {}
    all_paths = []

    for c in bdd._sat_iter(root, dict(), True):
        def_cost, att_cost = _eval_path_cost(c, ba, defenses, attacks)

        # Fill path with missing values
        for s in defenses + attacks:
            if s not in c:
                c[s] = False

        all_paths.append(c)

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

    # Add infty costs
    for def_vector in itertools.product([False, True], repeat=len(defenses)):
        def_dict = dict(zip(defenses, def_vector))

        # Check if `def_dict` is not found as a solution
        if not any(
            all(path[key] == value for key, value in def_dict.items())
            for path in all_paths
        ):
            def_cost = sum([ba[defense] for defense in def_dict if def_dict[defense]])
            pf.append((def_cost, float("inf")))

    pf = remove_dominated_pts("a", pf)

    return pf


def run(filepath, dump=False):
    ba = BasicAssignment(filepath)
    T = ADTree(filepath)
    defenses = T.get_basic_actions("d")
    attacks = T.get_basic_actions("a")

    start = timer()

    bdd = _bdd.BDD()
    bdd.configure(reordering=True)
    bdd.declare(*T.get_basic_actions())
    expr = T.get_boolean_expression()
    TREE = bdd.add_expr(expr)

    custom_order = {d: i for i, d in enumerate(defenses + attacks)}

    bdd.incref(TREE)

    if PRINT_PROGRESS:
        print(f"Initial size: {len(bdd)}")

    _bdd.reorder(bdd, custom_order)

    if dump:
        bdd.dump("./bdds/bdd_graph_custom_reorder.png", roots=[TREE])

    bdd.decref(TREE)

    if PRINT_PROGRESS:
        print(f"Size after custom-order: {len(bdd)}")

    pf = compute_pf(bdd, TREE, ba, defenses, attacks)

    print(pf)

    time = round((timer() - start) * 1000, 2)

    return time, pf


PRINT_PROGRESS = False

if __name__ == "__main__":
    # for i in [6, 12, 18, 24, 30]:
    #     time, _ = run(f"./trees_w_assignments/thesis_tree_{i}.xml")
    #     print(f"Time: {time} ms\n")

    time, _ = run("./trees_w_assignments/thesis_tree_24.xml")
    print(f"Time: {time} ms\n")
