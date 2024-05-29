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


def run_average(method, filepath, NO_RUNS=1):
    return sum(run(method, filepath)[0] for _ in range(0, NO_RUNS)) / NO_RUNS


PRINT_PROGRESS = False

if __name__ == "__main__":
    for i in [6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96]:
        filepath = f"./data/trees_w_assignments/tree_{i}.xml"
        print(os.path.basename(filepath))

        # Average time over `NO_RUNS`, excluding the time to read the tree
        time = run_average("bu", filepath)
        _, pf = run("bu", filepath)
        print(pf)

        print(f"Time: {time * 1000:.2f} ms.\n")

    # time, output = run("dummiest", "./data/trees_w_assignments/counter_example_dag.xml")
    # print(output)
    # print(f"Time: {time * 1000:.2f} ms.\n")
