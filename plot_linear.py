from __future__ import annotations

import matplotlib.pyplot as plt

from utils.util import read_results_from_csv


def plot(_x, _y, label):
    plt.plot(_x, _y, linestyle="--", marker="o", label=label)

    for i, y in enumerate(_y):

        if y < 1000:
            txt = f"{round(y, 2)} ms."
        elif y < 60000:
            txt = f"{round(y / 1000, 2)} s."
        elif y < 3.6e6:
            txt = f"{round(y / 60000, 2)} m."
        else:
            txt = f"{round(y/ 3.6e+6, 2)} h."

        plt.annotate(txt, (_x[i], y), textcoords="offset points", xytext=(0, -13))


def plot_results(x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values):
    plt.figure(figsize=(14, 6))

    plt.yscale("log")
    plt.xlabel("Tree size(defenses)")
    plt.xticks(range(len(x_labels)), x_labels)
    # plt.xticks(rotation=90)
    plt.ylabel("Runtime (ms)")

    plot(range(min(len(x_labels), len(dummiest_values))), dummiest_values, "dummiest")
    plot(range(min(len(x_labels), len(bilp_values))), bilp_values, "bilp")
    plot(range(min(len(x_labels), len(bdd_bu_values))), bdd_bu_values, "bdd_bu")
    plot(
        range(min(len(x_labels), len(bdd_all_values))),
        bdd_all_values,
        "bdd_all_paths",
    )

    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig("benchmark.png")


if __name__ == "__main__":
    labels, dummy, bilp, bdd_bu, bdd_all = read_results_from_csv(
        "./benchmarking/algorithm_linear.csv",
    )
    plot_results(labels, dummy, bilp, bdd_bu, bdd_all)
