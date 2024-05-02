import timeit

from adtrees.adtree import ADTree
from adtrees.attribute_domain import AttrDomain
from adtrees.basic_assignment import BasicAssignment
from copy import deepcopy


min_cost_attr = AttrDomain(min, sum, min, sum, 0, float('inf'))
filepath = './trees_w_assignments/thesis_tree_24.xml'
T = ADTree(filepath)
print(f'Tree size: {T.subtree_size()} (defenses: {len(T.get_basic_actions('d'))}, attacks: {len(T.get_basic_actions('a'))})')
print(f'Is tree-like ? {T.is_proper_tree()}')
print()
ba = BasicAssignment(filepath)

 
def measure_bu():
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    min_cost_attr.evaluate_bu(_T, _ba, True)
    t = timeit.Timer(lambda: min_cost_attr.evaluate_bu(_T, _ba, False))
    print("Time: {:.5f} ms.\n".format(t.timeit(50) / 50 * 1000))


def measure_dummy_bu():
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    t = timeit.Timer(lambda: min_cost_attr.evaluate_dummy_bu(_T, _ba, False))
    print("Time: {:.5f} ms.\n".format(t.timeit(1) / 1 * 1000))


def measure_dummiest():
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    t = timeit.Timer(lambda: min_cost_attr.evaluate_dummiest(_T, _ba, False))
    print("Time: {:.5f} ms.\n".format(t.timeit(1) / 1 * 1000))


measure_dummiest()

# measure_dummy_bu()

# measure_bu()
