import dd.bdd as _bdd

from adtrees.adtree import ADTree
from adtrees.attribute_domain import _reduce_pf_points
from adtrees.basic_assignment import BasicAssignment

from colorama import Fore, init

init(autoreset=True)

filepath = 'trees_w_assignments/counter_example_dag.xml'
ba = BasicAssignment(filepath)
T = ADTree(filepath)

bdd = _bdd.BDD()
bdd.configure(reordering=True)

bdd.declare('a1', 'a2', 'a3', 'd1', 'd2')
TREE = bdd.add_expr('(!d1 & a2) | (!(d1 | d2) & a1) | (!d2 & a3)')
custom_order = dict(
    d1=0, d2=1,
    a1=2, a2=3, a3=4)

# Infty-Tree
# bdd.declare('a1', 'a2', 'd1', 'd2')
# TREE = bdd.add_expr('(a1 & !d1) | (a2 & !d2)')
# custom_order = dict(
#     d1=0, d2=1,
#     a1=2, a2=3)

# Thesis-dag
# bdd.declare('SU', 'DNS', 'ACV', 'ESV', 'APUT', 'PA', 'BU', 'SKO', 'SDK')
# TREE = bdd.add_expr('((!(SU & !DNS) & ACV) | (!(SU & !DNS) & ESV) | (!APUT & PA) | BU) & (!SKO & SDK)')
# custom_order = dict(
#     SKO=0, APUT=1, SU=2,
#     DNS=3, ESV=4, ACV=5, PA=6, BU=7, SDK=9)

bdd.incref(TREE)

# print(STEAL_USER_DATA.to_expr())
# print(STEAL_USER_DATA.support)

# Print all models
# results = []

# for model in bdd.pick_iter(STEAL_USER_DATA):    
#     def_cost = sum([ba[d] for d in T.get_basic_actions('d') if d in model and model[d] == 1])
#     att_cost = sum([ba[a] for a in T.get_basic_actions('a') if a in model and model[a] == 1])
    
#     results.append((def_cost, att_cost))
#     print(f'{(def_cost, att_cost)}: {model}')

# results = sorted(results, key=lambda x: (x[0], x[1]))
# print(f'Results: {results}')

# results = _reduce_pf_points(T.root.type, results)
# print(f'PF: {results}')


bdd.collect_garbage()
# uses complemented edges in the ROBDD, where if your path passes a complemented dashed edge 
# and you reach a terminal node of 1, you should interpret it as a 0
bdd.dump('./bdds/bdd_graph.png', roots=[TREE])

print(f'Initial size: {len(bdd)}')

_bdd.reorder(bdd)
bdd.dump('./bdds/bdd_graph_optimal_reorder.png', roots=[TREE])

print(f'Size after optimal-order: {len(bdd)}')

_bdd.reorder(bdd, custom_order)
bdd.dump('./bdds/bdd_graph_custom_reorder.png', roots=[TREE])

print(f'Size after custom-order: {len(bdd)}')

bdd.decref(TREE)

idx2var = {k: v for v, k in bdd.vars.items()}

def walk_bdd(bdd, node_index, path: dict):
    # the tree is built around complements, which this doesn't account for yet
    var_i, low_ni, high_ni = bdd._succ[abs(node_index)]
    
    if not low_ni and not high_ni: # terminal
        print(Fore.GREEN + f'{_eval_path_cost(path)}, {path}')
        return
    
    label = f'{idx2var[var_i]}-{abs(node_index)}'
    
    print(f'{label}, {_eval_path_cost(path)}, {path}') 
    
    walk_bdd(bdd, low_ni, path | {label: False})
    walk_bdd(bdd, high_ni, path | {label: True})
    
def _eval_path_cost(path: dict):
    path = {k[:k.index("-")]: v for k,v in path.items()}
    
    def_cost = sum([ba[d] for d in T.get_basic_actions('d') if d in path and path[d]])
    att_cost = sum([ba[a] for a in T.get_basic_actions('a') if a in path and path[a]])
    return (def_cost, att_cost)
    
root_key = next(x for x in bdd._succ.keys() if bdd._succ[x][1] and bdd._succ[x][2])

# walk_bdd(bdd, root_key, path={})

def path_to_var(pbdd, path):
    return {bdd._level_to_var[i]: v
                for i, v in path.items()}

def _sat_iter(bdd, u, path, goal):
    """Recurse to enumerate models."""
    
    # Complemented edge, swap goal
    if u < 0:
        goal = not goal
        
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
    
    graph_label = f'{bdd._level_to_var[i]}-{abs(u)}'
    
    print(graph_label, path_to_var(bdd, path), goal)
    
    path_u_false = dict(path)
    path_u_false[i] = False
    
    path_u_true = dict(path)
    path_u_true[i] = True
    
    for x in _sat_iter(bdd, v, path_u_false, goal):
        yield x
    for x in _sat_iter(bdd, w, path_u_true, goal):
        yield x

i=0
for c in _sat_iter(bdd, TREE, dict(), True):
    i += 1
    print(Fore.GREEN + str(c))
    
print(f"Solutions : {i}")