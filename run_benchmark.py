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
    bu_values,
):
    with open(
        "./benchmarking/algorithm_results.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Tree Size(Defenses)", "Dummiest", "BILP", "BDD-BU", "BDD-ALL-DEF", "BU"],
        )

        for i, label in enumerate(labels):
            writer.writerow(
                [
                    label,
                    dummiest_values[i] if i < len(dummiest_values) else None,
                    bilp_values[i] if i < len(bilp_values) else None,
                    bdd_bu_values[i] if i < len(bdd_bu_values) else None,
                    bdd_all_values[i] if i < len(bdd_all_values) else None,
                    bu_values[i] if i < len(bu_values) else None,
                ],
            )


def eval_bu(file):
    time = run_bu("bu", file, 50)
    print(f"BU - finished {file}")
    return round(time * 1000, 2)


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


def eval_bdd_all_paths(file):
    time = run_bdd(file, 1, "all_paths")
    print(f"BDD-ALL-PATHS - finished {file}")
    return round(time * 1000, 2)


def eval_bdd_all_def(file):
    time = run_bdd(file, 1, "all_def")
    print(f"BDD-ALL-DEF - finished {file}")
    return round(time * 1000, 2)


if __name__ == "__main__":
    tree_linear_files = [
        f"./data/trees_w_assignments/tree_{i}.xml"
        for i in [9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 89, 97, 105, 113, 121, 129]
    ]
    dummy_x = [
        f"./data/trees_w_assignments/tree_{i}.xml" for i in [9, 17, 25, 33, 41, 49]
    ]

    RANDOM_TREES_PATH = "./data/random_trees/"
    random_tree_files = [
        join(RANDOM_TREES_PATH, f)
        for f in listdir(RANDOM_TREES_PATH)
        if isfile(join(RANDOM_TREES_PATH, f))
    ]

    files = tree_linear_files

    labels = []
    dummiest = []
    bilp = []
    bdd_bu = []
    bdd_all = []
    bu = []

    with ProcessPoolExecutor() as executor:
        # Collect dummiest values and x_labels using parallel execution
        dummiest = list(executor.map(eval_dummiest, files))

        # Collect bilp values
        bilp = list(executor.map(eval_bilp, files))

        # Collect bdd_bu values
        bdd_bu = list(executor.map(eval_bdd_bu, files))

        # Collect bdd_all_def values
        bdd_all = list(executor.map(eval_bdd_all_def, files))

        # Collect bu values
        bu = list(executor.map(eval_bu, files))

    for f in files:
        T = ADTree(f)
        tree_size = T.subtree_size()
        defense_count = len(T.get_basic_actions("d"))
        labels.append(f"{tree_size}({defense_count})")

    save_results_to_csv(labels, dummiest, bilp, bdd_bu, bdd_all, bu)
