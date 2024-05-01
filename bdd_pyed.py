from pyeda.inter import expr, expr2bdd, bddvar
from graphviz import Source

from adtrees.adtree import ADTree
from adtrees.attribute_domain import _reduce_pf_points
from adtrees.basic_assignment import BasicAssignment

filepath = "trees_w_assignments/thesis_dag.xml"
ba = BasicAssignment(filepath)
T = ADTree(filepath)

# formula_str = "(~d1 & a2) | (~(d1 | d2) & a1) | (~d2 & a3)" # counter_example_dag

# formula_str = "(~((d1 & d2) & ~a1) & a2) | a3" # thesis_tree

SU, DNS, ACV, ESV, APUT, PA, BU, SKO, SDK = map(
    bddvar, "SU DNS ACV ESV APUT PA BU SKO SDK".split()
)

formula_expr = ((~(SU & ~DNS) & ACV) | (~(SU & ~DNS) & ESV) | (~APUT & PA) | BU) & (
    ~SKO & SDK
)

point = {SU: 1, DNS: 1, ACV: 0, ESV: 1, SKO: 0, SDK: 1}
result = formula_expr.restrict(point).is_one()
print("The point is a solution:", result)

formula_bdd = expr2bdd(formula_expr)

formula_bdd_dot = formula_bdd.to_dot()
# print("BDD Nodes:", formula_bdd_dot)

results = []

for sat_raw in formula_bdd.satisfy_all():
    sat = {str(k): v for k, v in sat_raw.items()}

    def_cost = sum(
        [ba[d] for d in T.get_basic_actions("d") if d in sat and sat[d] == 1]
    )
    att_cost = sum(
        [ba[a] for a in T.get_basic_actions("a") if a in sat and sat[a] == 1]
    )

    results.append((def_cost, att_cost))

    # print(sat)

    print(f"{(def_cost, att_cost)}: {sat}")

# Sort first based on defense, and then on attack
results = sorted(results, key=lambda x: (x[0], x[1]))
print(f"Results: {results}")

results = _reduce_pf_points(T.root.type, results)
print(f"PF: {results}")

s = Source(formula_bdd_dot, filename="./bdds/bdd_pyed", format="png")
s.view()
