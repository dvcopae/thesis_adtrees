import dd.bdd as _bdd

from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment

from colorama import Fore, init

from timeit import default_timer as timer

from util.util import remove_dominated_pts

init(autoreset=True)


filepath = "trees_w_assignments/thesis_dag.xml"
ba = BasicAssignment(filepath)
T = ADTree(filepath)

defenses = T.get_basic_actions("d")
attacks = T.get_basic_actions("a")

start = timer()


def get_model_infty_tree():
    bdd = _bdd.BDD()
    bdd.configure(reordering=True)

    bdd.declare("a1", "a2", "d1", "d2")
    TREE = bdd.add_expr("(a1 & !d1) | (a2 & !d2)")
    custom_order = dict(d1=0, d2=1, a1=2, a2=3)

    bdd.incref(TREE)

    if PRINT_PROGRESS:
        print(f"Initial size: {len(bdd)}")

    _bdd.reorder(bdd, custom_order)

    # bdd.dump("./bdds/bdd_graph_custom_reorder.png", roots=[TREE])

    if PRINT_PROGRESS:
        print(f"Size after custom-order: {len(bdd)}")

    bdd.decref(TREE)

    return bdd, TREE


def get_model_counter_example_dag():
    bdd = _bdd.BDD()
    bdd.configure(reordering=True)

    bdd.declare("a1", "a2", "a3", "d1", "d2")
    TREE = bdd.add_expr("(!d1 & a2) | (!(d1 | d2) & a1) | (!d2 & a3)")
    custom_order = dict(d1=0, d2=1, a1=2, a2=3, a3=4)

    bdd.incref(TREE)

    if PRINT_PROGRESS:
        print(f"Initial size: {len(bdd)}")

    _bdd.reorder(bdd, custom_order)

    # bdd.dump("./bdds/bdd_graph_custom_reorder.png", roots=[TREE])

    if PRINT_PROGRESS:
        print(f"Size after custom-order: {len(bdd)}")

    bdd.decref(TREE)

    return bdd, TREE


def get_model_thesis_dag():
    bdd = _bdd.BDD()
    bdd.configure(reordering=True)

    bdd.declare("SU", "DNS", "ACV", "ESV", "APUT", "PA", "BU", "SKO", "SDK")
    TREE = bdd.add_expr(
        "((!(SU & !DNS) & ACV) | (!(SU & !DNS) & ESV) | (!APUT & PA) | BU) & (!SKO & SDK)"
    )
    custom_order = dict(SKO=0, APUT=1, SU=2, DNS=3, ESV=4, ACV=5, PA=6, BU=7, SDK=9)

    bdd.incref(TREE)

    if PRINT_PROGRESS:
        print(f"Initial size: {len(bdd)}")

    _bdd.reorder(bdd, custom_order)

    # bdd.dump("./bdds/bdd_graph_custom_reorder.png", roots=[TREE])

    if PRINT_PROGRESS:
        print(f"Size after custom-order: {len(bdd)}")

    bdd.decref(TREE)

    return bdd, TREE


def _eval_path_cost(path: dict):
    def_cost = sum([ba[d] for d in defenses if d in path and path[d]])
    att_cost = sum([ba[a] for a in attacks if a in path and path[a]])
    return (def_cost, att_cost)


def run(bdd, root):
    pf_dict = {}

    for c in bdd._sat_iter(root, dict(), True):
        def_cost, att_cost = _eval_path_cost(c)

        # Fill path with missing values
        for s in defenses + attacks:
            if s not in c:
                c[s] = False

        prev_path = pf_dict.get(def_cost)
        if prev_path:
            _, prev_att_cost = _eval_path_cost(prev_path)
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

    pf = [_eval_path_cost(c) for c in pf_dict.values()]
    pf = remove_dominated_pts("a", pf)

    time = round((timer() - start) * 1000, 2)

    return time, pf


PRINT_PROGRESS = False

bdd, root = get_model_thesis_dag()
time, pf = run(bdd, root)

print(pf)
print(f"Time: {time} ms\n")
