from copy import deepcopy
from timeit import default_timer as timer

from adtrees.adtree import ADTree
from adtrees.attribute_domain import AttrDomain
from adtrees.basic_assignment import BasicAssignment

min_cost_attr = AttrDomain(min, sum, min, sum, 0, float("inf"))


def measure_bu(T: ADTree, ba: BasicAssignment) -> float:
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    start = timer()
    pf = min_cost_attr.evaluate_bu(_T, _ba, False)
    return timer() - start, pf


def measure_dummy_bu(T: ADTree, ba: BasicAssignment) -> float:
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    start = timer()
    pf = min_cost_attr.evaluate_dummy_bu(_T, _ba, False)
    return timer() - start, pf


def measure_dummiest(T: ADTree, ba: BasicAssignment) -> float:
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    start = timer()
    pf = min_cost_attr.evaluate_dummiest(_T, _ba, False)
    return timer() - start, pf


def run(method, filepath):
    T = ADTree(filepath)

    ba = BasicAssignment(filepath)
    if method == "dummiest":
        return measure_dummiest(T, ba)
    elif method == "dummy-bu":
        return measure_dummy_bu(T, ba)
    elif method == "bu":
        return measure_bu(T, ba)


def run_average(method, filepath, NO_RUNS=100):
    return sum(run(method, filepath)[0] for _ in range(0, NO_RUNS)) / NO_RUNS


if __name__ == "__main__":
    # for i in [6, 12, 18, 24, 30, 36, 42, 48, 54]:
    #     filepath = f"./data/trees_w_assignments/tree_{i}.xml"
    #     print(os.path.basename(filepath))

    #     # Average time over `NO_RUNS`, excluding the time to read the tree
    #     time = run_average("bu", filepath)
    #     _, pf = run("bu", filepath)
    #     print(pf)

    #     print("Time: {:.2f} ms.\n".format(time * 1000))

    time, pf = run("dummiest", "./data/trees_w_assignments/tree_42.xml")
    print(pf)
    print("Time: {:.2f} ms.\n".format(time * 1000))
