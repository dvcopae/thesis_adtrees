import itertools
import sys
from timeit import default_timer as timer

from colorama import Fore, init
from gurobipy import GRB, LinExpr, Model

from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment
from utils.util import remove_dominated_pts, remove_low_att_pts

init(autoreset=True)


def warmup_bilp():
    m = Model("warmup")
    x = m.addVar(vtype=GRB.BINARY)
    y = m.addVar(vtype=GRB.BINARY)
    obj = 2 * x + 3 * y
    m.setObjective(-obj)  # maximize
    m.addConstr(x >= y)
    m.setParam(GRB.Param.OutputFlag, 0)
    m.optimize()


def get_model(T: ADTree, ba: BasicAssignment):
    m = Model("bilp")

    x_attacks = []
    x_deffs = []
    x_refinements = []

    # Maps the ADTree nodes labels to model variables
    model_vars = {}

    def get_inh_label(action: ADNode, counter: ADNode):
        return f"INH_{action.label}_{counter.label}"

    def check_unique_label(label, list):
        return len(list) == 0 or not any(l.label == label for l in list)

    def get_model_node(node: ADNode, check_inh=True):
        """
        This method should be used instead of `model_vars[node]` when
        using nodes which may have multiple labels
        """
        countered = check_inh and T.is_countered(node)
        label = (
            node.label if not countered else get_inh_label(node, T.get_counter(node))
        )

        return model_vars[label]

    attack_cost = LinExpr()
    defense_cost = LinExpr()

    # Add all nodes of the tree to BILP variables
    for ad_node in T.dict.keys():
        label = ad_node.label

        if ad_node.ref == "":  # basic step
            if ad_node.type == "a" and check_unique_label(label, x_attacks):
                x = m.addVar(vtype=GRB.BINARY, name=label)
                model_vars[label] = x
                x_attacks.append(ad_node)
                attack_cost.add(ba[ad_node.label] * get_model_node(ad_node, False))

            elif ad_node.type == "d" and check_unique_label(label, x_deffs):
                x = m.addVar(vtype=GRB.BINARY, name=label)
                model_vars[label] = x
                x_deffs.append(ad_node)
                defense_cost.add(ba[ad_node.label] * get_model_node(ad_node, False))

        elif check_unique_label(label, x_refinements):
            x_refinements.append(ad_node)
            x = m.addVar(vtype=GRB.BINARY, name=label)
            model_vars[label] = x

        countered = T.get_counter(ad_node)
        if countered:
            inh_label = get_inh_label(ad_node, countered)
            x = m.addVar(vtype=GRB.BINARY, name=inh_label)
            model_vars[inh_label] = x

    # Minimum damage objective
    m.setObjectiveN(attack_cost, index=0, priority=1, name="attack_cost")
    m.setObjectiveN(defense_cost, index=1, priority=0, name="defense_cost")

    # root is always reached
    m.addConstr(get_model_node(T.root) == 1, "root_is_reached")

    # We start from the bottom nodes to have the necessary variable as we go up the tree
    for ad_node in reversed(T.dict.keys()):
        model_node = get_model_node(ad_node, False)

        countered = T.get_counter(ad_node)
        if countered:  # INH gate
            x_inh_node = get_model_node(ad_node)
            inh_label = get_inh_label(ad_node, countered)
            # x_INH is attack * (1-counterattack)
            m.addConstr(
                x_inh_node == model_node * (1 - get_model_node(countered)),
                name=f"{inh_label}_ON",
            )
            # x_INH is 0 when attack is 0
            m.addConstr(x_inh_node <= model_node, name=f"{inh_label}_OFF")

        if ad_node.ref == "":  # basic event
            continue

        label_children = [
            (c.label, get_model_node(c))
            for c in T.get_children(ad_node)
            if not countered or c != countered
        ]
        children_sum_expr = LinExpr()
        children_sum_expr.addTerms(
            [1] * len(label_children), [c[1] for c in label_children]
        )

        if ad_node.ref == "AND":
            # x_AND must be 1 if all children are 1
            for c_label, c in label_children:
                m.addConstr(model_node <= c, name=f"{ad_node.label}_{c_label}")

            # Constraint that x_AND must be 0 if either child is 0
            m.addConstr(
                model_node >= children_sum_expr - (len(label_children) - 1),
                name=f"{ad_node.label}_bound",
            )
        elif ad_node.ref == "OR":
            # X_OR must be 1 if at least one child is 1
            for c_label, c in label_children:
                m.addConstr(model_node >= c, name=f"{ad_node.label}_{c_label}")

            # X_OR must be 0 if all children are 0
            m.addConstr(model_node <= children_sum_expr, name=f"{ad_node.label}_bound")

    m.setParam(GRB.Param.OutputFlag, 0)

    m.update()

    # m.write("model.lp")

    return m, defense_cost, attack_cost


def _add_exclusion_constraint(m, x_d, solution):
    """Add auxiliary constraints to ensure the defense is `solutions`"""

    for i, var in enumerate(x_d):
        constr_name = f"aux{i}"
        constraint = m.getConstrByName(constr_name)

        if constraint:
            # Update right hand side (after =) of solution
            constraint.RHS = solution[i]
        else:
            m.addConstr(var == solution[i], name=constr_name)


def _add_min_defense_constraint(m, defense_cost, min_defense_cost):
    if m.getConstrByName("def_cost_constr"):
        m.remove(m.getConstrByName("def_cost_constr"))
    m.addConstr(defense_cost >= min_defense_cost + 1e-5, "def_cost_constr")


def _add_min_atack_constraint(m, attack_cost, min_attack_cost):
    if m.getConstrByName("attack_cost_constr"):
        m.remove(m.getConstrByName("attack_cost_constr"))
    m.addConstr(attack_cost >= min_attack_cost + 1e-5, "attack_cost_constr")


def no_good_cut_method(m, defense_cost, attack_cost):
    results = []

    x_d = [defense_cost.getVar(i) for i in range(defense_cost.size())]

    # Keep track of last element
    last_def_cost = sys.maxsize
    last_att_cost = -sys.maxsize

    infty_vectors = []

    for def_vector in itertools.product([0, 1], repeat=defense_cost.size()):
        # def_vector must not `extend` any of the defense vectors which result in an infinity cost
        skip = False
        for iv in infty_vectors:
            if all(iv[i] == 0 or iv[i] == def_vector[i] for i in range(len(iv))):
                skip = True
                continue

        if skip:
            continue

        _add_exclusion_constraint(m, x_d, def_vector)

        m.optimize()

        if m.status != GRB.OPTIMAL:
            if 0 in def_vector:
                infty_vectors.append(def_vector)

            # Since we are adding the previous solutions instead of the current ones, the last one won't be added. Add it now.
            sol = (last_def_cost, last_att_cost)
            if sol not in results:
                if PRINT_PROGRESS:
                    print(Fore.GREEN + f"Added solution {sol}")
                results.append(sol)

            # Compute the defense cost manually, as the model has no solution for it
            x_def_coeffs = [
                defense_cost.getCoeff(i) for i in range(defense_cost.size())
            ]
            def_cost_output = sum(c * x for c, x in zip(x_def_coeffs, def_vector))

            sol = (def_cost_output, float("inf"))
            if PRINT_PROGRESS:
                print(Fore.GREEN + f"Added solution {sol}")
            results.append(sol)

            continue

        current_defense_cost = defense_cost.getValue()
        current_attack_cost = m.objVal

        if PRINT_PROGRESS:
            print(
                Fore.GREEN
                + f"Found solution {current_defense_cost, current_attack_cost}"
            )
            print(
                ", ".join(
                    [
                        f"{v.varName}: {int(abs(v.x))}"
                        for v in m.getVars()
                        if not v.varName.startswith("aux_")
                    ]
                )
            )

        results.append((current_defense_cost, current_attack_cost))  # Record solution

        last_att_cost = current_attack_cost
        last_def_cost = current_defense_cost

    return results


def run(filepath):
    T = ADTree(filepath)
    tree_size = T.subtree_size()
    defense_count = len(T.get_basic_actions("d"))

    ba = BasicAssignment(filepath)

    start = timer()

    m, defense_cost, attack_cost = get_model(T, ba)

    results = no_good_cut_method(m, defense_cost, attack_cost)

    results_pf = remove_low_att_pts("a", results)
    results_pf = remove_dominated_pts("a", results_pf)

    if PRINT_PROGRESS:
        print(Fore.RED + f"Removed {list(set(results) - set(results_pf))}")

    time = timer() - start
    return time, results_pf, tree_size, defense_count


PRINT_PROGRESS = False


def run_average(filepath, NO_RUNS=10):
    warmup_bilp()
    return sum(run(filepath)[0] for _ in range(0, NO_RUNS)) / NO_RUNS


if __name__ == "__main__":
    print("===== BILP =====\n")

    # for i in [6, 12, 18, 24, 30, 36, 42, 48, 54]:
    #     filepath = f"./data/trees_w_assignments/tree_{i}.xml"
    #     print(os.path.basename(filepath))

    #     # Average time over `NO_RUNS`, excluding the time to read the tree
    #     time = run_average(filepath)

    #     print("Time: {:.2f} ms.\n".format(time * 1000))

    time, pf, _, _ = run("./data/trees_w_assignments/tree_72.xml")
    print(pf)
    print("Time: {:.2f} ms.\n".format(time * 1000))

    # cProfile.run('run(f"./data/trees_w_assignments/tree_24.xml")')
