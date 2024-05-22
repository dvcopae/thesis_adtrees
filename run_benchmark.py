from __future__ import annotations

import csv
from concurrent.futures import ProcessPoolExecutor
from os import listdir
from os.path import isfile
from os.path import join

from adtrees.adtree import ADTree
from bdd import run_average as run_bdd
from bilp import run_average as run_bilp
from bu import run_average as run_bu


def save_results_to_csv(
    labels,
    dummiest_values,
    bilp_values,
    bdd_bu_values,
    bdd_all_values,
):
    with open(
        "./benchmarking/algorithm_results.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Tree Size(Defenses)", "Dummiest", "BILP", "BDD-BU", "BDD-ALL"],
        )

        for i, label in enumerate(labels):
            writer.writerow(
                [
                    label,
                    dummiest_values[i] if i < len(dummiest_values) else None,
                    bilp_values[i] if i < len(bilp_values) else None,
                    bdd_bu_values[i] if i < len(bdd_bu_values) else None,
                    bdd_all_values[i] if i < len(bdd_all_values) else None,
                ],
            )


def eval_dummiest(file):
    time = run_bu("dummiest", file, 1)
    print(f"Dummiest - finished {file}")
    return round(time * 1000, 2)


def eval_bilp(file):
    time = run_bilp(file, 1)
    print(f"BILP - finished {file}")
    return round(time * 1000, 2)


def eval_bdd_bu(file):
    time = run_bdd(file, 50, "bu")
    print(f"BDD-BU - finished {file}")
    return round(time * 1000, 2)


def eval_bdd_all(file):
    time = run_bdd(file, 50, "all_paths")
    print(f"BDD-ALL - finished {file}")
    return round(time * 1000, 2)


if __name__ == "__main__":
    tree_linear_files = [
        f"./data/trees_w_assignments/tree_{i}.xml"
        for i in [6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96]
    ]
    dummy_x = [
        f"./data/trees_w_assignments/tree_{i}.xml" for i in [6, 12, 18, 24, 30, 36]
    ]

    RANDOM_TREES_PATH = "./data/random_trees/"
    random_tree_files = [
        join(RANDOM_TREES_PATH, f)
        for f in listdir(RANDOM_TREES_PATH)
        if isfile(join(RANDOM_TREES_PATH, f))
    ]

    files = random_tree_files

    labels = []
    dummiest = []
    bilp = []
    bdd_bu = []
    bdd_all = []

    with ProcessPoolExecutor() as executor:
        # Collect dummiest values and x_labels using parallel execution
        dummiest = list(executor.map(eval_dummiest, files))

        # Collect bilp values
        # bilp_values = list(executor.map(eval_bilp, files))

        # Collect bdd values
        bdd_bu = list(executor.map(eval_bdd_bu, files))

        # Collect bdd values
        # bdd_all_values = list(executor.map(eval_bdd_all, files))

    for f in files:
        T = ADTree(f)
        tree_size = T.subtree_size()
        defense_count = len(T.get_basic_actions("d"))
        labels.append(f"{tree_size}({defense_count})")

    save_results_to_csv(
        labels,
        dummiest,
        bilp,
        bdd_bu,
        bdd_all,
    )
