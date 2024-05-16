import matplotlib.pyplot as plt

from util.util import read_results_from_csv


def plot_results(x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values):
    plt.yscale("log")
    plt.xscale("log")

    axis_upper_limit = max(bilp_values + bdd_bu_values)
    axis_lower_limit = min(bilp_values + bdd_bu_values)

    # Add some padding
    axis_lower_limit = axis_lower_limit * 0.7
    axis_upper_limit = axis_upper_limit * 1.3

    plt.xlim(axis_lower_limit, axis_upper_limit)
    plt.ylim(axis_lower_limit, axis_upper_limit)

    plt.xlabel("bdd_bu runtime (ms)")
    plt.ylabel("bilp runtime (ms)")
    plt.scatter(bdd_bu_values, bilp_values, marker="x")
    plt.tight_layout()
    plt.savefig("bddbu_bilp.png")


if __name__ == "__main__":
    x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values = (
        read_results_from_csv("./benchmarking/algorithm_results.csv")
    )
    plot_results(x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values)
