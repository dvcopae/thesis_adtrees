from __future__ import annotations

import itertools
import sys
from timeit import default_timer as timer

from colorama import Fore
from colorama import init
from gurobipy import GRB
from gurobipy import LinExpr
from gurobipy import Model

from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.basic_assignment import BasicAssignment
from utils.util import remove_dominated_pts
from utils.util import remove_low_att_pts

init(autoreset=True)


def warmup_bilp() -> None:
    """Gurobi takes a bit more time on its first run, so account for this when doing benchmarks."""
    m = Model("warmup")
    x = m.addVar(vtype=GRB.BINARY)
    y = m.addVar(vtype=GRB.BINARY)
    m.setObjective(-2 * x - 3 * y)
    m.addConstr(x >= y)
    m.setParam(GRB.Param.OutputFlag, 0)
    m.optimize()


def get_model(
    T: ADTree,
    ba: BasicAssignment,
    dump: bool = False,
) -> tuple[Model, LinExpr, LinExpr]:
    """
    Create the BILP model.

    Parameters:
        T (ADTree): The attack-defense tree.
        ba (BasicAssignment): The basic assignment.
        dump (bool): Write the model to a file.

    Returns:
        Tuple[Model, LinExpr, LinExpr]: The BILP model,
        defense cost, and attack cost linear expressions.
    """
    m = Model("bilp")

    x_attacks = []
    x_deffs = []
    x_refinements = []

    attack_cost = LinExpr()
    defense_cost = LinExpr()
    # Maps the ADTree nodes labels to Gurobi model variables
    model_vars: dict[str, LinExpr] = {}

    def get_inh_label(action: ADNode, counter: ADNode) -> str:
        return f"INH_{action.label}_{counter.label}"

    def check_unique_label(label: ADNode, elements: list) -> bool:
        """Check if label is unique in the list."""
        return len(elements) == 0 or not any(l.label == label for l in elements)

    def get_model_node(node: ADNode, check_inh: bool = True) -> LinExpr:
        """
        This method should be used instead of `model_vars[node]` when
        using nodes which may have multiple labels
        """
        countered = check_inh and T.is_countered(node)
        label = (
            node.label if not countered else get_inh_label(node, T.get_counter(node))
        )

        return model_vars[label]

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
            x_inh_node = get_model_node(ad_node, True)
            inh_label = get_inh_label(ad_node, countered)
            # x_INH is attack * (1-counterattack)
            m.addConstr(
                x_inh_node <= 1 - get_model_node(countered),
                name=f"{inh_label}_ON",
            )
            m.addConstr(
                x_inh_node >= model_node - get_model_node(countered),
                name=f"{inh_label}_IDK",
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
            [1] * len(label_children),
            [c[1] for c in label_children],
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

    # if dump:
    m.write("model.lp")

    return m, defense_cost, attack_cost


def _add_exclusion_constraint(m: Model, x_d: list[LinExpr], solution) -> None:
    """Add auxiliary constraints to ensure the defense is `solutions`"""

    for i, var in enumerate(x_d):
        constr_name = f"aux{i}"
        constraint = m.getConstrByName(constr_name)

        if constraint:
            # Update right hand side (after =) of solution
            constraint.RHS = solution[i]
        else:
            m.addConstr(var == solution[i], name=constr_name)


def compute_pf(m: Model, defense_cost: LinExpr) -> list[tuple[float, float]]:
    results = []

    x_d = [defense_cost.getVar(i) for i in range(defense_cost.size())]

    # Keep track of last element
    last_def_cost = sys.maxsize
    last_att_cost = -sys.maxsize

    infty_vectors = []

    for def_vector in itertools.product([0, 1], repeat=defense_cost.size()):
        # def_vector must not `extend` any of the defense vectors which result in an infinity cost
        if any(
            all(iv[i] == 0 or iv[i] == def_vector[i] for i in range(len(iv)))
            for iv in infty_vectors
        ):
            continue

        _add_exclusion_constraint(m, x_d, def_vector)
        m.optimize()

        if m.status != GRB.OPTIMAL:
            if 0 in def_vector:
                infty_vectors.append(def_vector)

            # Since we are adding the previous solutions instead of the
            # current ones, the last one won't be added. Add it now.
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
                + f"Found solution {current_defense_cost, current_attack_cost}",
            )
            print(
                ", ".join(
                    [
                        f"{v.varName}: {int(abs(v.x))}"
                        for v in m.getVars()
                        if not v.varName.startswith("aux_")
                    ],
                ),
            )

        results.append((current_defense_cost, current_attack_cost))  # Record solution

        last_att_cost = current_attack_cost
        last_def_cost = current_defense_cost

    return results


def run(filepath: str) -> tuple[float, list[tuple[float, float]], int, int]:
    T = ADTree(filepath)
    ba = BasicAssignment(filepath)

    start = timer()

    m, defense_cost, _ = get_model(T, ba)

    results = compute_pf(m, defense_cost)

    results = remove_low_att_pts(results)
    results = remove_dominated_pts(results)

    if PRINT_PROGRESS:
        print(Fore.RED + f"Removed {list(set(results) - set(results))}")

    time_elapsed = timer() - start
    return time_elapsed, results, T.subtree_size(), len(T.get_basic_actions("d"))


def run_average(filepath, no_runs=1):
    warmup_bilp()
    return sum(run(filepath)[0] for _ in range(0, no_runs)) / no_runs


PRINT_PROGRESS = False

if __name__ == "__main__":
    print("===== BILP =====\n")

    # for i in [6, 12, 18, 24, 30, 36, 42]:
    #     filepath = f"./data/trees_w_assignments/tree_{i}.xml"
    #     print(os.path.basename(filepath))

    #     # Average time over `NO_RUNS`, excluding the time to read the tree
    #     time = run_average(filepath)
    #     pf = run(filepath)[1]
    #     print(pf)

    #     print("Time: {:.2f} ms.\n".format(time * 1000))

    time, pf, _, _ = run("./data/trees_w_assignments/defensive_pareto_deff.xml")
    print(pf)
    print(f"Time: {time * 1000:.2f} ms.\n")
