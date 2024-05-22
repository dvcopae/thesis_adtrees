from pathlib import Path
from matplotlib import patches
import matplotlib.pyplot as plt
import numpy

from utils.util import read_results_from_csv


def size_to_color(n):
    return n // 20


def plot_results(x_labels, x, y, output):
    plt.yscale("log")
    plt.xscale("log")

    # First 5 colors of the `plasma` colormap
    color_mapping = {
        0: [0.050383, 0.029803, 0.527975, 1.0],
        1: [4.17642e-01, 5.64000e-04, 6.58390e-01, 1.00000e00],
        2: [0.69284, 0.165141, 0.564522, 1.0],
        3: [0.881443, 0.392529, 0.383229, 1.0],
        4: [0.98826, 0.652325, 0.211364, 1.0],
        5: [0.940015, 0.975158, 0.131326, 1.0],
    }

    # Apply colors based on size categories
    colors = [color_mapping[size_to_color(int(l.partition("(")[0]))] for l in x_labels]

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
        patches.Patch(facecolor=color_mapping[i], label=f"< {(i+1) * 20}")
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

    # BDD <-> BILP
    filename = "./benchmarking/algorithm_bdd_bilp.csv"
    x_labels, _, bilp_values, bdd_bu_values, _ = read_results_from_csv(filename)
    plot_results(x_labels, bdd_bu_values, bilp_values, get_plot_filename(filename))

    # BDD <-> BU
    filename = "./benchmarking/algorithm_bdd_bu.csv"
    x_labels, dummiest_values, _, bdd_bu_values, _ = read_results_from_csv(filename)
    plot_results(x_labels, bdd_bu_values, dummiest_values, get_plot_filename(filename))

    # BDD <-> dummiest
    filename = "./benchmarking/algorithm_bdd_dummy.csv"
    x_labels, dummiest_values, _, bdd_bu_values, _ = read_results_from_csv(filename)
    plot_results(x_labels, bdd_bu_values, dummiest_values, get_plot_filename(filename))
