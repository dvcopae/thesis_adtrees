import timeit

from adtrees.adtree import ADTree
from adtrees.attribute_domain import AttrDomain
from adtrees.basic_assignment import BasicAssignment


min_cost_attr = AttrDomain(min, sum, min, sum, 0, float('inf'))
filepath = 'trees_w_assignments/rfid_dag_modified.xml'
T = ADTree(filepath)
print(f'Tree size: {T.subtree_size()} (defenses: {len(T.get_basic_actions('d'))}, attacks: {len(T.get_basic_actions('a'))})')
print(f'Is tree-like ? {T.is_proper_tree()}')
ba = BasicAssignment(filepath)


def measure_bu():
    min_cost_attr.evaluate_bu(T, ba, True)
    t = timeit.Timer(lambda: min_cost_attr.evaluate_bu(T, ba, False))
    print("Time: {:.5f} ms.".format(t.timeit(50) / 50 * 1000))


def measure_dummy_bu():
    t = timeit.Timer(lambda: min_cost_attr.evaluate_dummy_bu(T, ba, True))
    print("Time: {:.5f} ms.".format(t.timeit(1) / 1 * 1000))


def measure_dummiest():
    t = timeit.Timer(lambda: min_cost_attr.evaluate_dummiest(T, ba, True))
    print("Time: {:.5f} ms.".format(t.timeit(1) / 1 * 1000))


# measure_dummiest()

measure_dummy_bu()

# measure_bu()
