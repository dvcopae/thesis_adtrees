from __future__ import annotations

import itertools
import os
from timeit import default_timer as timer

import dd.bdd as _bdd
from colorama import Fore
from colorama import init

from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment
from utils.util import remove_dominated_pts
from utils.util import remove_low_att_pts

init(autoreset=True)


def _eval_path_cost(
    path: dict[str, bool],
    ba: BasicAssignment,
    defenses: list[str],
    attacks: list[str],
) -> tuple[float, float]:
    def_cost = sum(ba[d] for d in defenses if d in path and path[d])
    att_cost = sum(ba[a] for a in attacks if a in path and path[a])
    return def_cost, att_cost


pf_storage = {}


def compute_pf_bu(
    bdd: _bdd.BDD,
    u: int,
    defenses: list[str],
    ba: BasicAssignment,
    root_type: str,
    goal: bool = True,
) -> list[tuple[float, float]]:
    # Avoid revisiting nodes
    if u in pf_storage:
        return pf_storage[u]

    p = abs(u)

    # Complemented edge, swap goal
    if u < 0:
        goal = not goal

    # terminal ?
    if p == 1:
        if root_type == "a":
            return [(0, 0)] if goal else [(0, float("inf"))]
        else:
            return [(0, float("inf"))] if goal else [(0, 0)]

    # non-terminal
    i, v, w = bdd._succ[p]
    assert v and w, "Invalid BDD structure"

    pf_left = compute_pf_bu(bdd, v, defenses, ba, root_type, goal)
    pf_right = compute_pf_bu(bdd, w, defenses, ba, root_type, goal)

    # Taking a `right` edge means we activated `u`, so add it's cost
    u_label = bdd._level_to_var[i]
    is_defense = u_label in defenses

    if is_defense:
        pf_right = [(d + ba[u_label], a) for d, a in pf_right]
    else:
        pf_right = [(d, a + ba[u_label]) for d, a in pf_right]

    pf = pf_left + pf_right

    if is_defense:  # necessary for counter_example_dag
        pf = remove_dominated_pts(pf)
    else:
        cost_dict = {}
        for point in pf:
            def_cost = point[0]
            att_cost = point[1]
            if def_cost not in cost_dict or att_cost < cost_dict[def_cost]:
                cost_dict[def_cost] = att_cost

        pf = list(cost_dict.items())

    pf_storage[u] = pf

    return pf


failed_paths = []


def find_all_paths_bdd(bdd: _bdd.BDD, u, root_type: str, path=None, goal=True):
    """Recurse to enumerate models."""

    if not path:
        path = {}

    p = abs(u)

    # Complemented edge, swap goal
    if u < 0:
        goal = not goal

    # terminal ?
    if p == 1:
        path_dict = {bdd._level_to_var[i]: v for i, v in path.items()}

        goal_is_reached = goal if root_type == "a" else not goal

        if goal_is_reached:
            yield path_dict
        else:
            failed_paths.append(path_dict)
        return

    # non-terminal
    i, v, w = bdd._succ[p]
    assert v and w, "Invalid BDD structure"

    path_u_false = dict(path)
    path_u_false[i] = False

    path_u_true = dict(path)
    path_u_true[i] = True

    yield from find_all_paths_bdd(bdd, v, root_type, path_u_false, goal)
    yield from find_all_paths_bdd(bdd, w, root_type, path_u_true, goal)


def compute_pf_all_paths(
    bdd: _bdd.BDD,
    root: ADNode,
    ba: BasicAssignment,
    defenses: list[str],
    attacks: list[str],
    root_type: str,
) -> list[tuple[float, float]]:
    global failed_paths
    pf_dict = {}
    failed_paths = []

    for c in find_all_paths_bdd(bdd, root, root_type):
        def_cost, att_cost = _eval_path_cost(c, ba, defenses, attacks)

        # Fill path with missing defenses, and keep track of
        # which defense configurations we encountered
        for s in defenses + attacks:
            c.setdefault(s, False)

        prev_path = pf_dict.get(def_cost)
        if prev_path:
            _, prev_att_cost = _eval_path_cost(prev_path, ba, defenses, attacks)
            if all(prev_path[d] == c[d] for d in defenses):
                if att_cost < prev_att_cost:
                    # We have the same defense vector as the current solution -> MINIMIZE att_cost
                    pf_dict[def_cost] = c
            elif att_cost > prev_att_cost:
                # We found another defense vector which has the same def_cost -> MAXIMIZE att_cost
                pf_dict[def_cost] = c
        else:
            # Value not in dict, add it
            pf_dict[def_cost] = c

        if PRINT_PROGRESS:
            print(Fore.GREEN + f"{(def_cost, att_cost)} {c}")

    pf = [_eval_path_cost(c, ba, defenses, attacks) for c in pf_dict.values()]

    # If a path fails and it doesn't pass any attacks, then it must block all attacks
    infinity_paths = [p for p in failed_paths if not any(k in attacks for k in p)]
    infinity_costs = [
        (_eval_path_cost(p, ba, defenses, attacks)[0], float("inf"))
        for p in infinity_paths
    ]
    pf.extend(infinity_costs)

    pf = remove_dominated_pts(pf)
    return pf


def run_all_def(
    boolean_expr: str,
    defenses: list[str],
    attacks: list[str],
    ba: BasicAssignment,
    root_type: str,
):

    start = timer()
    results = []
    for def_vector in itertools.product([0, 1], repeat=len(defenses)):
        def_expr = boolean_expr
        def_dict = dict(zip(defenses, def_vector))
        for k, v in def_dict.items():
            def_expr = def_expr.replace(str(k), str(bool(v)))

        bdd = _bdd.BDD()
        bdd.declare(*attacks)
        root = bdd.add_expr(def_expr)
        def_cost = sum(ba[d] for d in defenses if d in def_dict and def_dict[d])

        def_vector_pf = [
            (def_cost, a) for _, a in compute_pf_bu(bdd, root, [], ba, root_type)
        ]
        results.extend(def_vector_pf)

    results = remove_low_att_pts(results)
    results = remove_dominated_pts(results)

    time_elapsed = timer() - start
    return time_elapsed, results


def run(filepath, method="bu", dump=False):
    # reset pf_Storage for bdd_bu
    global pf_storage
    pf_storage = {}

    ba = BasicAssignment(filepath)
    tree = ADTree(filepath)
    defenses = tree.get_basic_actions("d")
    attacks = tree.get_basic_actions("a")

    start = timer()

    expr = tree.get_boolean_expression()

    if method == "all_def":
        return run_all_def(expr, defenses, attacks, ba, tree.root.type)

    bdd = _bdd.BDD()
    bdd.configure(reordering=False)
    bdd.declare(*(defenses + attacks))
    root = bdd.add_expr(expr)
    custom_order = {d: i for i, d in enumerate(defenses + attacks)}

    if PRINT_PROGRESS:
        print(f"Initial size: {len(bdd)}")

    _bdd.reorder(bdd, custom_order)

    if dump:
        bdd.dump("./bdds/bdd_graph_custom_reorder.png", roots=[root])

    if PRINT_PROGRESS:
        print(f"Size after custom-order: {len(bdd)}")

    pf = []
    if method == "bu":
        pf = compute_pf_bu(bdd, root, defenses, ba, tree.root.type)
    elif method == "all_paths":
        pf = compute_pf_all_paths(bdd, root, ba, defenses, attacks, tree.root.type)

    elapsed_time = timer() - start

    return elapsed_time, pf


def run_average(filepath: str, no_runs: int = 50, method: str = "bu") -> float:
    return sum(run(filepath, method)[0] for _ in range(0, no_runs)) / no_runs


PRINT_PROGRESS = False

if __name__ == "__main__":
    print("===== BDD =====\n")
    for i in [90, 96]:
        filepath = f"./data/trees_w_assignments/tree_{i}.xml"
        print(os.path.basename(filepath))

        # Average time over `NO_RUNS`, excluding the time to read the tree
        time = run_average(filepath, no_runs=1, method="all_paths")
        _, pf = run(filepath)
        print(pf)

        print(f"Time: {time * 1000:.2f} ms.\n")

    # time, output = run(
    #     "./data/trees_w_assignments/counter_example_dag.xml",
    #     method="bu",
    #     dump=True,
    # )
    # print(output)
    # print(f"Time: {time * 1000:.2f} ms.\n")
