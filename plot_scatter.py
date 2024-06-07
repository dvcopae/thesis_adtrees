from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy
from matplotlib import patches

from utils.util import read_results_from_csv


def size_to_color(n):
    return n // 50


def plot_results(labels, x, y, output):
    plt.yscale("log")
    plt.xscale("log")

    color_mapping = {
        0: "darkred",
        1: "darkorange",
        # 2: "yellow",
        # 3: "darkgreen",
        # 4: "darkcyan",
        # 5: "darkblue",
        # 6: "darkviolet",
    }

    # Apply colors based on size categories
    colors = [color_mapping[size_to_color(int(l.partition("(")[0]))] for l in labels]

    lower_limit = 10**-2.5
    upper_limit = 10**6.5

    plt.xlim(lower_limit, upper_limit)
    plt.ylim(lower_limit, upper_limit)

    plt.xlabel(f"{output.split('_')[1]} runtime (ms)")
    plt.ylabel(f"{output.split('_')[2]} runtime (ms)")

    plt.scatter(x, y, c=colors, marker="x")

    diagonal_x = numpy.linspace(lower_limit, upper_limit, 100)
    diagonal_y = diagonal_x

    plt.plot(diagonal_x, diagonal_y, color="black", linewidth=1)

    legend_elements = [
        patches.Patch(facecolor=color_mapping[i], label=f"< {(i+1) * 50}")
        for i in range(len(color_mapping))
    ]
    legend = plt.legend(
        handles=legend_elements,
        fontsize="small",
        loc="lower right",
        title="Tree size",
        fancybox=True,
    )

    frame = legend.get_frame()  # sets up for color, edge, and transparency
    frame.set_facecolor("#E5E4E2")  # color of legend
    frame.set_edgecolor("black")  # edge color of legend
    frame.set_alpha(1)  # deals with transparency

    plt.tight_layout()
    plt.savefig(f"{output}.png")
    plt.clf()


if __name__ == "__main__":

    def get_plot_filename(f):
        output = Path(f).stem
        output = (
            "plot_" + output[output.index("_") + 1 :]
        )  # get everything after the first _
        return output

    # # BDD_BU <-> BILP
    FILENAME = "./benchmarking/algorithm_bdd-bu_bilp.csv"
    x_labels, _, bilp_values, bdd_bu_values, _, _, _ = read_results_from_csv(FILENAME)
    plot_results(x_labels, bdd_bu_values, bilp_values, get_plot_filename(FILENAME))

    # # BILP <-> BU
    # FILENAME = "./benchmarking/algorithm_bu_bilp.csv"
    # x_labels, _, bilp_values, _, _, bu_values, _ = read_results_from_csv(FILENAME)
    # plot_results(x_labels, bu_values, bilp_values, get_plot_filename(FILENAME))

    # BDD_BU <-> BU
    # FILENAME = "./benchmarking/algorithm_bu_bdd-bu.csv"
    # x_labels, _, _, bdd_bu_values, _, bu_values, _ = read_results_from_csv(FILENAME)
    # plot_results(x_labels, bu_values, bdd_bu_values, get_plot_filename(FILENAME))
