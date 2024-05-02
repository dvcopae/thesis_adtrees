import timeit

from adtrees.adtree import ADTree
from adtrees.attribute_domain import AttrDomain
from adtrees.basic_assignment import BasicAssignment
from copy import deepcopy


min_cost_attr = AttrDomain(min, sum, min, sum, 0, float('inf'))
 
def measure_bu(T, ba):
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    min_cost_attr.evaluate_bu(_T, _ba, True)
    t = timeit.Timer(lambda: min_cost_attr.evaluate_bu(_T, _ba, False))
    time = round(t.timeit(50) / 50 * 1000, 2)
    return time


def measure_dummy_bu(T, ba):
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    t = timeit.Timer(lambda: min_cost_attr.evaluate_dummy_bu(_T, _ba, False))
    time = round(t.timeit(1) / 1 * 1000, 2)
    return time    


def measure_dummiest(T, ba):
    _T = deepcopy(T)
    _ba = deepcopy(ba)
    t = timeit.Timer(lambda: min_cost_attr.evaluate_dummiest(_T, _ba, False))
    time = round(t.timeit(1) / 1 * 1000, 2)
    return time


def run(method, filepath):
    T = ADTree(filepath)
    print(f'Tree size: {T.subtree_size()} (defenses: {len(T.get_basic_actions('d'))}, attacks: {len(T.get_basic_actions('a'))})')
    ba = BasicAssignment(filepath)
    if method=='dummiest':
        time = measure_dummiest(T, ba)
    elif method=='dummy-bu':
        time = measure_dummy_bu(T, ba)
    elif method=='bu':
        time = measure_bu(T, ba)
    
    return time

if __name__ == "__main__":
    # for i in [6,12,18,24,30]:    
    #     time = run('dummiest', f'./trees_w_assignments/thesis_tree_{i}.xml')
    #     print(f'Time: {time} ms\n')

    run('dummiest', './trees_w_assignments/thesis_tree_36.xml')
