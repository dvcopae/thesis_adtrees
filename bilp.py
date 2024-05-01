import itertools
from re import X
from gurobipy import Model, GRB, quicksum
import sys
from timeit import default_timer as timer
from colorama import Fore, init

from util.util import remove_low_att_pts, remove_dominated_pts

init(autoreset=True)

start = timer()
results = []


def get_model_small_dag():
    m = Model("bilp")

    x_a1 = m.addVar(vtype=GRB.BINARY, name="x_a1")
    x_a2 = m.addVar(vtype=GRB.BINARY, name="x_a2")
    x_a3 = m.addVar(vtype=GRB.BINARY, name="x_a3")
    x_a4 = m.addVar(vtype=GRB.BINARY, name="x_a4")
    x_a5 = m.addVar(vtype=GRB.BINARY, name="x_a5")

    x_d1 = m.addVar(vtype=GRB.BINARY, name="x_d1")
    x_d2 = m.addVar(vtype=GRB.BINARY, name="x_d2")

    x_OR1 = m.addVar(vtype=GRB.BINARY, name="x_OR1")
    x_OR2 = m.addVar(vtype=GRB.BINARY, name="x_OR2")

    x_INH_OR1_d1 = m.addVar(vtype=GRB.BINARY, name="x_INH_OR1_d1")
    x_INH_OR2_d2 = m.addVar(vtype=GRB.BINARY, name="x_INH_OR2_d2")
    x_INH_d1_a3 = m.addVar(vtype=GRB.BINARY, name="x_INH_d1_a3")
    x_INH_d2_a5 = m.addVar(vtype=GRB.BINARY, name="x_INH_d2_a5")

    x_AND = m.addVar(vtype=GRB.BINARY, name="x_AND")  # root

    attack_cost = 4 * x_a1 + 8 * x_a2 + 16 * x_a3 + 8 * x_a4 + 100 * x_a5
    defense_cost = 2 * x_d1 + 4 * x_d2

    # Minimum damage objective
    m.setObjectiveN(attack_cost, index=0, priority=1)
    m.setObjectiveN(defense_cost, index=1, priority=0)

    # root is always reached
    m.addConstr(x_AND == 1, "root_is_reached")

    # each OR node has as many constraints as children,
    # and one "upper_bound" to ensure that when all children are false, OR should be false
    # m.addConstr(x_OR1 >= x_a1, "OR1_a1")
    # m.addConstr(x_OR1 >= x_a2, "OR1_a2")
    m.addConstr(x_OR1 <= x_a1 + x_a2, "OR1_upper_bound")

    # m.addConstr(x_OR2 >= x_a1, "OR2_a1")
    # m.addConstr(x_OR2 >= x_a4, "OR2_a4")
    m.addConstr(x_OR2 <= x_a1 + x_a4, "OR2_upper_bound")

    # INH constraints: INH = attack * (1-counterattack)
    # and INH is disabled when attack is disabled
    m.addConstr(x_INH_OR1_d1 == x_OR1 * (1 - x_INH_d1_a3), "INH_OR1_d1_success")
    m.addConstr(x_INH_OR1_d1 <= x_OR1, "INH_inactive_if_OR1_inactive")

    m.addConstr(x_INH_OR2_d2 == x_OR2 * (1 - x_INH_d2_a5), "INH_OR2_d2_success")
    m.addConstr(x_INH_OR2_d2 <= x_OR2, "INH_inactive_if_OR2_inactive")

    m.addConstr(x_INH_d1_a3 == x_d1 * (1 - x_a3), "INH_d1_a3_success")
    m.addConstr(x_INH_d1_a3 <= x_d1, "INH_inactive_if_d1_inactive")

    m.addConstr(x_INH_d2_a5 == x_d2 * (1 - x_a5), "INH_d2_a5_success")
    m.addConstr(x_INH_d2_a5 <= x_d2, "INH_inactive_if_d1_inactive")

    # AND has a single constraint: if it's activated, all nodes must be activated as well
    m.addConstr(x_AND <= x_INH_OR1_d1)
    m.addConstr(x_AND <= x_INH_OR2_d2)
    m.addConstr(x_AND >= x_INH_OR1_d1 + x_INH_OR2_d2 - 1)

    m.setParam(GRB.Param.OutputFlag, 0)

    m.update()

    # Save problem
    # m.write("small_dag.lp")

    return m, defense_cost, attack_cost


def get_model_infty_tree():
    m = Model("bilp")

    x_a1 = m.addVar(vtype=GRB.BINARY, name="a1")
    x_a2 = m.addVar(vtype=GRB.BINARY, name="a2")

    x_d1 = m.addVar(vtype=GRB.BINARY, name="d1")
    x_d2 = m.addVar(vtype=GRB.BINARY, name="d2")

    x_INH_a1_d1 = m.addVar(vtype=GRB.BINARY, name="x_INH_a1_d1")
    x_INH_a2_d2 = m.addVar(vtype=GRB.BINARY, name="x_INH_a2_d2")

    x_OR = m.addVar(vtype=GRB.BINARY, name="x_OR")  # root

    attack_cost = 1 * x_a1 + 2 * x_a2
    defense_cost = 10 * x_d1 + 10 * x_d2

    # Minimum damage objective
    m.setObjectiveN(attack_cost, index=0, priority=1)
    m.setObjectiveN(defense_cost, index=1, priority=0)

    # root is always reached
    m.addConstr(x_OR == 1)

    # each OR node has as many constraints as children,
    # and one "upper_bound" to ensure that when all children are false, OR should be false
    m.addConstr(x_OR >= x_INH_a1_d1)
    m.addConstr(x_OR >= x_INH_a2_d2)
    m.addConstr(x_OR <= x_INH_a1_d1 + x_INH_a2_d2)

    # INH constraints: INH = attack * (1-counterattack)
    # and INH is disabled when attack is disabled
    m.addConstr(x_INH_a1_d1 == x_a1 * (1 - x_d1))
    m.addConstr(x_INH_a1_d1 <= x_a1)

    m.addConstr(x_INH_a2_d2 == x_a2 * (1 - x_d2))
    m.addConstr(x_INH_a2_d2 <= x_a2)

    m.setParam(GRB.Param.OutputFlag, 0)

    m.update()

    # Save problem
    # m.write("infty_tree.lp")

    return m, defense_cost, attack_cost


def get_model_counter_example_dag():
    m = Model("bilp")

    x_a1 = m.addVar(vtype=GRB.BINARY, name="a1")
    x_a2 = m.addVar(vtype=GRB.BINARY, name="a2")
    x_a3 = m.addVar(vtype=GRB.BINARY, name="a3")

    x_d1 = m.addVar(vtype=GRB.BINARY, name="d1")
    x_d2 = m.addVar(vtype=GRB.BINARY, name="d2")

    x_D_OR = m.addVar(vtype=GRB.BINARY, name="x_D_OR")

    x_INH_a2_d1 = m.addVar(vtype=GRB.BINARY, name="x_INH_a2_d1")
    x_INH_a3_d2 = m.addVar(vtype=GRB.BINARY, name="x_INH_a3_d2")
    x_INH_a1_D_OR = m.addVar(vtype=GRB.BINARY, name="x_INH_a1_D_OR")

    x_A_OR = m.addVar(vtype=GRB.BINARY, name="x_A_OR")  # root

    attack_cost = 2 * x_a2 + 1 * x_a1 + 3 * x_a3
    defense_cost = 10 * x_d1 + 10 * x_d2

    # Minimum damage objective
    m.setObjectiveN(attack_cost, index=0, priority=0)
    m.setObjectiveN(defense_cost, index=1, priority=0)

    # root is always reached
    m.addConstr(x_A_OR == 1)

    # each OR node has as many constraints as children -> without it you get scenarios where child=1 but or=0
    # and one "upper_bound" to ensure that when all children are false, OR should be false -> without it, you get scenario where all children =0, but or=1
    m.addConstr(x_D_OR >= x_d1)
    m.addConstr(x_D_OR >= x_d2)
    m.addConstr(x_D_OR <= x_d1 + x_d2)

    m.addConstr(x_A_OR >= x_INH_a2_d1)
    m.addConstr(x_A_OR >= x_INH_a3_d2)
    m.addConstr(x_A_OR >= x_INH_a1_D_OR)
    m.addConstr(x_A_OR <= x_INH_a2_d1 + x_INH_a3_d2 + x_INH_a1_D_OR)

    # INH constraints: INH = attack * (1-counterattack)
    # and INH is disabled when attack is disabled
    m.addConstr(x_INH_a1_D_OR == x_a1 * (1 - x_D_OR))
    m.addConstr(x_INH_a1_D_OR <= x_a1)

    m.addConstr(x_INH_a2_d1 == x_a2 * (1 - x_d1))
    m.addConstr(x_INH_a2_d1 <= x_a2)

    m.addConstr(x_INH_a3_d2 == x_a3 * (1 - x_d2))
    m.addConstr(x_INH_a3_d2 <= x_a3)

    m.setParam(GRB.Param.OutputFlag, 0)  # disable logging

    m.update()

    # Save problem
    # m.write("infty_tree.lp")

    return m, defense_cost, attack_cost


def get_aaa_model():
    m = Model("bilp")

    x_a1 = m.addVar(vtype=GRB.BINARY, name="a1")

    x_d1 = m.addVar(vtype=GRB.BINARY, name="d1")
    x_d2 = m.addVar(vtype=GRB.BINARY, name="d2")

    x_AND = m.addVar(vtype=GRB.BINARY, name="x_AND")

    x_INH_a1_d1 = m.addVar(vtype=GRB.BINARY, name="x_INH_a1_d1")  # root

    attack_cost = 1 * x_a1
    defense_cost = 10 * x_d1 + 10 * x_d2

    # Minimum damage objective
    m.setObjectiveN(attack_cost, index=0, priority=1)
    m.setObjectiveN(defense_cost, index=1, priority=0)

    # root is always reached
    m.addConstr(x_INH_a1_d1 == 1)

    # INH constraints: INH = attack * (1-counterattack)
    # and INH is disabled when attack is disabled
    m.addConstr(x_INH_a1_d1 == x_a1 * (1 - x_AND))
    m.addConstr(x_INH_a1_d1 <= x_a1)

    # x_AND must be 1 if both x_d1 and x_d2 are 1
    m.addConstr(x_AND <= x_d1)
    m.addConstr(x_AND <= x_d2)
    # Constraint that x_AND must be 0 if either x_d1 or x_d2 is 0
    m.addConstr(x_AND >= x_d1 + x_d2 - 1)

    m.setParam(GRB.Param.OutputFlag, 0)

    m.update()

    # Save problem
    # m.write("infty_tree.lp")

    return m, defense_cost, attack_cost


def _add_exclusion_constraint(m, x_d, solution):
    """Add auxiliary constraints to ensure the current defenses do not repeat"""
    aux_vars = [m.addVar(vtype=GRB.BINARY, name=f"aux_{i}") for i in range(len(x_d))]
    m.update()

    for i, var in enumerate(x_d):
        if solution[i] == 1:
            m.addConstr(
                aux_vars[i] == 1 - var
            )  # If enabled, set to the opposite of solution[i]
        else:
            m.addConstr(aux_vars[i] == var)  # If disabled, don't change anything

    # at least one of the auxiliary variables is true
    m.addConstr(quicksum(aux_vars) >= 1, "exclusion")


def _add_min_defense_constraint(m, min_defense_cost):
    if m.getConstrByName("def_cost_constr"):
        m.remove(m.getConstrByName("def_cost_constr"))
    m.addConstr(defense_cost >= min_defense_cost + 1e-5, "def_cost_constr")


def _add_min_atack_constraint(m, min_attack_cost):
    if m.getConstrByName("attack_cost_constr"):
        m.remove(m.getConstrByName("attack_cost_constr"))
    m.addConstr(attack_cost >= min_attack_cost + 1e-5, "attack_cost_constr")


def _print_current_solution(m):
    def_c = defense_cost.getValue()
    att_c = m.objVal
    _printif(Fore.GREEN + f"Found solution {def_c, att_c}")
    _printif(
        ", ".join(
            [
                f"{v.varName}: {int(abs(v.x))}"
                for v in m.getVars()
                if not v.varName.startswith("aux_")
            ]
        )
    )


def _printif(s):
    if PRINT_PROGRESS:
        print(s)


def no_good_cut_method(m, defense_cost):
    prev_def_vectors = []
    x_d = [defense_cost.getVar(i) for i in range(defense_cost.size())]

    # Keep track of last element
    last_def_cost = sys.maxsize
    last_att_cost = -sys.maxsize

    while True:
        m.optimize()
        if m.status != GRB.OPTIMAL:
            # Since we are adding the previous solutions instead of the current ones, the last one won't be added. Add it now.
            sol = (last_def_cost, last_att_cost)
            if sol not in results:
                _printif(Fore.GREEN + f"Added solution {sol}")
                results.append(sol)

            # Add the next possible output of the function `defense_cost` and infty to the results
            x_def_coeffs = [
                defense_cost.getCoeff(i) for i in range(defense_cost.size())
            ]

            for combination in itertools.product([0, 1], repeat=len(x_def_coeffs)):
                def_cost_output = sum(c * x for c, x in zip(x_def_coeffs, combination))
                if def_cost_output > last_def_cost:
                    sol = (def_cost_output, float("inf"))
                    _printif(Fore.GREEN + f"Added solution {sol}")
                    results.append(sol)
                    break

            _printif("No more feasible solutions.")
            break

        current_defense_cost = defense_cost.getValue()
        current_attack_cost = m.objVal

        def_vec = [int(var.x) for var in x_d]

        # Check if the solution is new
        if def_vec not in prev_def_vectors:
            _print_current_solution(m)
            results.append(
                (current_defense_cost, current_attack_cost)
            )  # Record solution

            # Add exclusion for the current solution
            prev_def_vectors.append(def_vec)

            _add_exclusion_constraint(m, x_d, def_vec)

            # # Update the constraints to push for higher minimum attack cost
            # if current_attack_cost > last_att_cost and current_defense_cost <= last_def_cost:
            #     _add_min_atack_constraint(m, last_att_cost)

            last_att_cost = current_attack_cost
            last_def_cost = current_defense_cost

        else:
            _printif("Duplicate solution found, terminating...")
            break


PRINT_PROGRESS = True

# m, defense_cost, attack_cost = get_model_small_dag()

# m, defense_cost, attack_cost = get_model_infty_tree()

m, defense_cost, attack_cost = get_model_counter_example_dag()

# m, defense_cost, attack_cost = get_aaa_model()

no_good_cut_method(m, defense_cost)

results_pf = remove_low_att_pts("a", results)
results_pf = remove_dominated_pts("a", results_pf)

_printif(Fore.RED + f"Removed {list(set(results) - set(results_pf))}")
print("Results: " + str(results_pf))
print("Time: {:.5f} ms.\n".format((timer() - start) * 1000))
