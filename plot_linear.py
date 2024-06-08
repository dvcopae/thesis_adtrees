from __future__ import annotations

import matplotlib.pyplot as plt

from utils.util import read_results_from_csv


def plot(_x, _y, label):
    plt.plot(_x, _y, linestyle="--", marker="o", label=label)

    # Annotate just the last point in _y, otherwise the graph gets too crowded
    y = _y[-1]

    if y < 1:
        txt = f"{round(y * 1000, 2)} ms."
    elif y < 60:
        txt = f"{round(y, 2)} s."
    elif y < 3600:
        txt = f"{round(y / 60, 2)} m."
    else:
        txt = f"{round(y/ 3600, 2)} h."

    plt.annotate(txt, (_x[len(_y) - 1], y), textcoords="offset points", xytext=(0, -13))

    # for i, y in enumerate(_y):
    #     if y < 1000:
    #         txt = f"{round(y, 2)} ms."
    #     elif y < 60000:
    #         txt = f"{round(y / 1000, 2)} s."
    #     elif y < 3.6e6:
    #         txt = f"{round(y / 60000, 2)} m."
    #     else:
    #         txt = f"{round(y/ 3.6e+6, 2)} h."

    #     plt.annotate(txt, (_x[i], y), textcoords="offset points", xytext=(0, -13))


def plot_results(
    x_labels,
    dummiest_values,
    bilp_values,
    bdd_bu_values,
    bdd_all_def_values,
    bu_values,
    bdd_all_paths,
):
    plt.figure(figsize=(10, 6))

    plt.yscale("log")
    # plt.xlabel("Tree size(defenses)")
    plt.xticks(range(len(x_labels)), x_labels)
    plt.xticks(rotation=90)
    # plt.ylabel("Runtime (ms)")

    # Transform from ms to s
    dummiest_values = [v / 1000 for v in dummiest_values]
    bilp_values = [v / 1000 for v in bilp_values]
    bdd_bu_values = [v / 1000 for v in bdd_bu_values]
    bdd_all_def_values = [v / 1000 for v in bdd_all_def_values]
    bu_values = [v / 1000 for v in bu_values]
    bdd_all_paths = [v / 1000 for v in bdd_all_paths]

    plot(range(min(len(x_labels), len(bu_values))), bu_values, "BU")
    plot(range(min(len(x_labels), len(dummiest_values))), dummiest_values, "Naive")
    plot(range(min(len(x_labels), len(bilp_values))), bilp_values, "BILP")
    plot(range(min(len(x_labels), len(bdd_all_paths))), bdd_all_paths, "BDD_PATHS")
    plot(
        range(min(len(x_labels), len(bdd_all_def_values))),
        bdd_all_def_values,
        "BDD_ALL_DEF",
    )
    plot(range(min(len(x_labels), len(bdd_bu_values))), bdd_bu_values, "BDD_BU")

    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig("benchmark.png")


if __name__ == "__main__":
    labels, dummy, bilp, bdd_bu, bdd_all_def, bu, bdd_all_paths = read_results_from_csv(
        "./benchmarking/algorithm_linear.csv",
    )
    plot_results(labels, dummy, bilp, bdd_bu, bdd_all_def, bu, bdd_all_paths)
