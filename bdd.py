import itertools
import os
import timeit
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


def _sat_iter(bdd, u, path, goal):
    """Recurse to enumerate models."""

    # Complemented edge, swap goal
    if u < 0:
        goal = not goal

    def path_to_var(pbdd, path):
        return {bdd._level_to_var[i]: v for i, v in path.items()}

    # terminal ?
    if abs(u) == 1:
        if goal:
            yield path_to_var(bdd, path)
        return

    # non-terminal
    i, v, w = bdd._succ[abs(u)]
    if not v:
        raise AssertionError(v)
    if not w:
        raise AssertionError(w)

    path_u_false = dict(path)
    path_u_false[i] = False

    path_u_true = dict(path)
    path_u_true[i] = True

    for x in _sat_iter(bdd, v, path_u_false, goal):
        yield x
    for x in _sat_iter(bdd, w, path_u_true, goal):
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

    for c in _sat_iter(bdd, root, dict(), True):
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
    bdd.configure(reordering=False)
    bdd.declare(*(defenses + attacks))
    expr = T.get_boolean_expression()
    TREE = bdd.add_expr(expr)

    custom_order = {d: i for i, d in enumerate(defenses + attacks)}

    bdd.incref(TREE)

    if PRINT_PROGRESS:
        print(f"Initial size: {len(bdd)}")

    _bdd.reorder(bdd, order=custom_order)

    if dump:
        bdd.dump("./bdds/bdd_graph_custom_reorder.png", roots=[TREE])

    bdd.decref(TREE)

    if PRINT_PROGRESS:
        print(f"Size after custom-order: {len(bdd)}")

    pf = compute_pf_all_paths(bdd, TREE, ba, defenses, attacks)

    time = timer() - start

    return time, pf


PRINT_PROGRESS = False


def run_average(filepath, NO_RUNS=100):
    return sum(run(filepath)[0] for _ in range(0, NO_RUNS)) / NO_RUNS


if __name__ == "__main__":
    print("===== BDD =====\n")
    for i in [6, 12, 18, 24, 30, 36]:
        filepath = f"./trees_w_assignments/thesis_tree_{i}.xml"
        print(os.path.basename(filepath))

        # Average time over `NO_RUNS`, excluding the time to read the tree
        time = run_average(filepath)

        print("Time: {:.2f} ms.\n".format(time * 1000))

    time, _ = run_average("./trees_w_assignments/thesis_tree_36.xml")
    print("Time: {:.2f} ms.\n".format(time * 1000))
