from __future__ import annotations

import os
from copy import deepcopy
from timeit import default_timer as timer

from adtrees.adtree import ADTree
from adtrees.attribute_domain import AttrDomain
from adtrees.basic_assignment import BasicAssignment

min_cost_attr = AttrDomain(min, sum, min, sum, 0, float("inf"))


def measure_bu(tree: ADTree, ba: BasicAssignment) -> float:
    _tree = deepcopy(tree)
    _ba = deepcopy(ba)
    start = timer()
    pf = min_cost_attr.evaluate_bu(_tree, _ba, PRINT_PROGRESS)
    return timer() - start, pf


def measure_dummy_bu(tree: ADTree, ba: BasicAssignment) -> float:
    _tree = deepcopy(tree)
    _ba = deepcopy(ba)
    start = timer()
    pf = min_cost_attr.evaluate_dummy_bu(_tree, _ba, PRINT_PROGRESS)
    return timer() - start, pf


def measure_dummiest(tree: ADTree, ba: BasicAssignment) -> float:
    _tree = deepcopy(tree)
    _ba = deepcopy(ba)
    start = timer()
    pf = min_cost_attr.evaluate_dummiest(_tree, _ba, PRINT_PROGRESS)
    return timer() - start, pf


def run(method, filepath):
    tree = ADTree(filepath)

    ba = BasicAssignment(filepath)
    if method == "dummiest":
        return measure_dummiest(tree, ba)

    if method == "dummy-bu":
        return measure_dummy_bu(tree, ba)

    if method == "bu":
        return measure_bu(tree, ba)


def run_average(method, filepath, NO_RUNS=50):
    return sum(run(method, filepath)[0] for _ in range(0, NO_RUNS)) / NO_RUNS


PRINT_PROGRESS = False

if __name__ == "__main__":
    for i in [9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 89, 97, 105, 113, 121, 129]:
        filepath = f"./data/trees_w_assignments/tree_{i}.xml"
        print(os.path.basename(filepath))

        # Average time over `NO_RUNS`, excluding the time to read the tree
        time = run_average("bu", filepath, 100)
        _, pf = run("bu", filepath)
        print(pf)

        print(f"Time: {time * 1000:.2f} ms.\n")

    # time, output = run("bu", "./data/trees_w_assignments/thesis_tree_modified.xml")
    # print(output)
    # print(f"Time: {time * 1000:.2f} ms.\n")
