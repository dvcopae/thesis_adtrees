import timeit

from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.attribute_domain import AttrDomain
from adtrees.basic_assignment import BasicAssignment


# r = ADNode('a', 'break in', 'OR')
# x1 = ADNode('a', 'break in through the back door')
# x2 = ADNode('a', 'break in through one of the windows')
# y1 = ADNode('d', 'install lock on the back door')
# d = {r: [x1, x2], x1: [y1], x2: [], y1: []}
# T = ADTree(dictionary=d)
# ba_def = BasicAssignment()
# ba_att = BasicAssignment()
#
# ba_att['break in through the back door'] = 1
# ba_att['break in through one of the windows'] = 2
# ba_def['install lock on the back door'] = 1

def plus_op(x, y):
    return x + y


min_cost_attr = AttrDomain(min, plus_op, min, plus_op)
filepath = 'trees_w_assignments/rfid_large_80_modified.xml'

T = ADTree(filepath)
# print(f'Tree size: {T.subtree_size(T.root)}')
ba = BasicAssignment(filepath)

min_cost_attr.evaluate_bu(T, ba, True)

t = timeit.Timer(lambda: min_cost_attr.evaluate_bu(T, ba, False))
print("Time: {:.5f} ms.".format(t.timeit(100)/100*1000))


