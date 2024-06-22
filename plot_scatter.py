from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy
from matplotlib import patches

from utils.util import read_results_from_csv


def size_to_color(n):
    return n // 50


def plot_results(labels, x, y, output, label_loc="lower right"):

    # From ms. to s.
    x = [v / 1000 for v in x]
    y = [v / 1000 for v in y]

    plt.figure(figsize=(4, 3))
    plt.xlabel("Time (s)")
    plt.ylabel("Time (s)")
    plt.yscale("log")
    plt.xscale("log")

    color_mapping = {
        0: "darkred",
        1: "darkorange",
        2: "yellow",
        3: "darkgreen",
        4: "darkcyan",
        5: "darkblue",
        6: "darkviolet",
    }

    colors = [size_to_color(int(l.partition("(")[0])) for l in labels]

    # Delete all the extra colors from the mapping
    for k in list(color_mapping.keys()):
        if k > max(colors):
            del color_mapping[k]

    # Apply colors based on size categories
    colors = [color_mapping[c] for c in colors]

    lower_limit = 10**-6
    upper_limit = 10**4

    plt.xlim(lower_limit, upper_limit)
    plt.ylim(lower_limit, upper_limit)

    # plt.xlabel(f"{output.split('_')[1]} runtime (ms)")
    # plt.ylabel(f"{output.split('_')[2]} runtime (ms)")

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
        loc=label_loc,
        title="Tree size",
        fancybox=True,
    )

    frame = legend.get_frame()  # sets up for color, edge, and transparency
    frame.set_facecolor("#E5E4E2")  # color of legend
    frame.set_edgecolor("black")  # edge color of legend
    frame.set_alpha(1)  # deals with transparency

    plt.tight_layout()
    plt.savefig(f"{output}.pdf")
    plt.clf()


if __name__ == "__main__":

    def get_plot_filename(f):
        output = Path(f).stem
        output = (
            "plot_" + output[output.index("_") + 1 :]
        )  # get everything after the first _
        return output

    # BDD_BU <-> BILP
    FILENAME = "./benchmarking/algorithm_bdd-bu_bilp.csv"
    x_labels, _, bilp_values, bdd_bu_values, _, _, _ = read_results_from_csv(FILENAME)
    plot_results(x_labels, bdd_bu_values, bilp_values, get_plot_filename(FILENAME))

    # BILP <-> BU
    FILENAME = "./benchmarking/algorithm_bu_bilp.csv"
    x_labels, _, bilp_values, _, _, bu_values, _ = read_results_from_csv(FILENAME)
    plot_results(x_labels, bu_values, bilp_values, get_plot_filename(FILENAME))

    # BDD_BU <-> BU
    FILENAME = "./benchmarking/algorithm_bu_bdd-bu.csv"
    x_labels, _, _, bdd_bu_values, _, bu_values, _ = read_results_from_csv(FILENAME)
    plot_results(x_labels, bu_values, bdd_bu_values, get_plot_filename(FILENAME))

    ######## DUMMIEST ###########

    # Dummiest <-> BDD_BU
    FILENAME = "./benchmarking/algorithm_dummiest_bdd-bu.csv"
    x_labels, dummiest_values, _, bdd_bu_values, _, _, _ = read_results_from_csv(
        FILENAME,
    )
    plot_results(
        x_labels,
        dummiest_values,
        bdd_bu_values,
        get_plot_filename(FILENAME),
        "upper left",
    )

    # Dummiest <-> BILP
    FILENAME = "./benchmarking/algorithm_dummiest_bilp.csv"
    x_labels, dummiest_values, bilp_values, _, _, _, _ = read_results_from_csv(FILENAME)
    plot_results(
        x_labels,
        dummiest_values,
        bilp_values,
        get_plot_filename(FILENAME),
        "upper left",
    )

    # Dummiest <-> BU
    FILENAME = "./benchmarking/algorithm_dummiest_bu.csv"
    x_labels, dummiest_values, _, _, _, bu_values, _ = read_results_from_csv(FILENAME)
    plot_results(
        x_labels,
        dummiest_values,
        bu_values,
        get_plot_filename(FILENAME),
        "upper left",
    )

    ######## BDD ###########
    # BDD_BU <-> BDD_PATHS
    FILENAME = "./benchmarking/algorithm_bdd-bu_bdd-paths.csv"
    x_labels, _, _, bdd_bu_values, _, _, bdd_paths_values = read_results_from_csv(
        FILENAME,
    )
    plot_results(x_labels, bdd_bu_values, bdd_paths_values, get_plot_filename(FILENAME))

    # BDD_BU <-> BDD_ALL_DEF
    FILENAME = "./benchmarking/algorithm_bdd-bu_bdd-all-def.csv"
    x_labels, _, _, bdd_bu_values, bdd_all_def_values, _, _ = read_results_from_csv(
        FILENAME,
    )
    plot_results(
        x_labels,
        bdd_bu_values,
        bdd_all_def_values,
        get_plot_filename(FILENAME),
    )

    # BDD_PATHS <-> BDD_ALL_DEF
    FILENAME = "./benchmarking/algorithm_bdd-paths_bdd-all-def.csv"
    x_labels, _, _, _, bdd_all_def_values, _, bdd_paths_values = read_results_from_csv(
        FILENAME,
    )
    plot_results(
        x_labels,
        bdd_paths_values,
        bdd_all_def_values,
        get_plot_filename(FILENAME),
    )
