import itertools
from gurobipy import Model, GRB, quicksum
import sys
from timeit import default_timer as timer

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

    x_AND = m.addVar(vtype=GRB.BINARY, name="x_AND") # root

    attack_cost = 4*x_a1 + 8*x_a2 + 16*x_a3 + 8*x_a4 + 100*x_a5
    defense_cost = 2*x_d1 + 4*x_d2

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
    m.addConstr((x_AND == 1) >> (x_INH_OR1_d1 + x_INH_OR2_d2 == 2), "root_AND")

    m.setParam(GRB.Param.OutputFlag, 0)
    
    m.update()  

    # Save problem
    m.write("small_dag.lp")
    
    return m, defense_cost, attack_cost

def get_model_infty_tree():
    m = Model("bilp")

    x_a1 = m.addVar(vtype=GRB.BINARY)
    x_a2 = m.addVar(vtype=GRB.BINARY)

    x_d1 = m.addVar(vtype=GRB.BINARY)
    x_d2 = m.addVar(vtype=GRB.BINARY)

    x_INH_a1_d1 = m.addVar(vtype=GRB.BINARY)
    x_INH_a2_d2 = m.addVar(vtype=GRB.BINARY)

    x_OR = m.addVar(vtype=GRB.BINARY) # root

    attack_cost = 1*x_a1 + 2*x_a2
    defense_cost = 10*x_d1 + 10*x_d2

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
    m.write("infty_tree.lp")
    
    return m, defense_cost, attack_cost
  
def _add_exclusion_constraint(m, x_d, solution):
    """Add auxiliary constraints to ensure the current defenses do not repeat"""
    aux_vars = [m.addVar(vtype=GRB.BINARY, name=f"aux_{i}") for i in range(len(x_d))]
    m.update()

    for i, var in enumerate(x_d):
        if solution[i] == 1:
            m.addConstr(aux_vars[i] == 1 - var)  # If enabled, set to the opposite of solution[i]
        else:
            m.addConstr(aux_vars[i] == var)  # If disabled, don't change anything

    # at least one of the auxiliary variables is true
    m.addConstr(quicksum(aux_vars) >= 1, "exclusion")

def no_good_cut_method(m, defense_cost, attack_cost):
    """
    DOESN'T WORK WHEN DIFFERENT DEFENSE ACTIVATIONS SHARE THE SAME DEFENSE_SUM
    
    Find PF by iteratively finding a feasible solution, adding a constraint to remove that 
    solution from the feasible region, and then find the next feasible solution, 
    until no more solutions are met.
    """
    
    previous_defenses = []
    x_d = [defense_cost.getVar(i) for i in range(defense_cost.size())]
    while True:
        m.optimize()
        if m.status != GRB.OPTIMAL:
            print("No more feasible solutions.")
            break

        current_defense = [int(var.x) for var in x_d]
        
        # Check if the solution is new
        if current_defense not in previous_defenses:
            previous_defenses.append(current_defense)
            current_defense_cost = defense_cost if isinstance(defense_cost, float) else defense_cost.getValue()
            current_attack_cost = m.objVal

            # Add exclusion for the current solution
            _add_exclusion_constraint(m, x_d, current_defense)
            
            results.append((current_defense_cost, current_attack_cost))
        else:
            print("Duplicate solution found, terminating...")
            break

    return previous_defenses

def epsilon_constraint_method(m, defense_cost, attack_cost):
    """Find PF by placing repeteadly placing a constraint on the defense cost, 
    and then optimizing the attack cost.
    https://groups.google.com/g/gurobi/c/0AoQIqg6-UA/m/qWEw1R_wAAAJ
    """
    
    x_def_coeffs = [defense_cost.getCoeff(i) for i in range(defense_cost.size())]
    epsilon_values = []

    # Generate all possible combinations of binary values for the variables
    for combination in itertools.product([0, 1], repeat=len(x_def_coeffs)):
        epsilon_values.append(sum(c * x for c, x in zip(x_def_coeffs, combination)))

    epsilon_values = sorted(set(epsilon_values))
    last_attack_cost = 0
    
    for epsilon in epsilon_values:
        m.addConstr(defense_cost == epsilon, "epsilon_def_constr")
        # can't model strict inequality, so just add a very small value
        m.addConstr(attack_cost >= last_attack_cost + 1e-5, "attack_cost_constr") 
        m.optimize()
        
        if m.status == GRB.OPTIMAL:
            results.append((defense_cost.getValue(), attack_cost.getValue()))
            last_attack_cost = attack_cost.getValue()
            m.remove(m.getConstrByName("epsilon_def_constr"))
            m.remove(m.getConstrByName("attack_cost_constr"))
        else:
            results.append((epsilon, float('inf')))
            print(f"No solution for defense_cost == {epsilon}")

# m, defense_cost, attack_cost = get_model_small_dag()

m, defense_cost, attack_cost = get_model_infty_tree()

# no_good_cut_method(m, defense_cost, attack_cost)

epsilon_constraint_method(m, defense_cost, attack_cost)

print("Results:", results)
print("Time: {:.5f} ms.\n".format((timer() - start)*1000))