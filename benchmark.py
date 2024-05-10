from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
import csv

from adtrees.adtree import ADTree
from bu import run_average as run_bu
from bilp import run_average as run_bilp
from bdd import run_average as run_bdd

x = [6, 12, 18, 24, 30, 36, 42, 48]
dummy_x = [i for i in x if i <= 36]

x_labels = []
dummiest_values = []
bilp_values = []
bdd_bu_values = []
bdd_all_values = []


def save_results_to_csv(
    x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values
):
    with open("./benchmarks/algorithm_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Tree Size(Defenses)", "Dummiest", "BILP", "BDD-BU", "BDD-ALL"]
        )

        for i in range(len(x_labels)):
            writer.writerow(
                [
                    x_labels[i],
                    dummiest_values[i] if i < len(dummiest_values) else None,
                    bilp_values[i],
                    bdd_bu_values[i],
                    bdd_all_values[i],
                ]
            )


def eval_dummiest(i):
    time = run_bu("dummiest", f"./trees_w_assignments/tree_{i}.xml", 1)
    print(f"Dummiest - finished {i}")
    return round(time * 1000, 2)


def eval_bilp(i):
    time = run_bilp(f"./trees_w_assignments/tree_{i}.xml", 1)
    print(f"BILP - finished {i}")
    return round(time * 1000, 2)


def eval_bdd_bu(i):
    time = run_bdd(f"./trees_w_assignments/tree_{i}.xml", 50, "bu")
    print(f"BDD-BU - finished {i}")
    return round(time * 1000, 2)


def eval_bdd_all(i):
    time = run_bdd(f"./trees_w_assignments/tree_{i}.xml", 50, "all_paths")
    print(f"BDD-ALL - finished {i}")
    return round(time * 1000, 2)


if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        # Collect dummiest values and x_labels using parallel execution
        dummiest_values = list(executor.map(eval_dummiest, dummy_x))

        # Collect bilp values
        bilp_values = list(executor.map(eval_bilp, x))

        # Collect bdd values
        bdd_bu_values = list(executor.map(eval_bdd_bu, x))

        # Collect bdd values
        bdd_all_values = list(executor.map(eval_bdd_all, x))

    for i in x:
        T = ADTree(f"./trees_w_assignments/tree_{i}.xml")
        tree_size = T.subtree_size()
        defense_count = len(T.get_basic_actions("d"))
        x_labels.append(f"{tree_size}({defense_count})")

    save_results_to_csv(
        x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values
    )
