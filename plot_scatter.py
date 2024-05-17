from pathlib import Path
import matplotlib.pyplot as plt
import numpy

from utils.util import read_results_from_csv


def plot_results(x_labels, x, y, output):
    plt.yscale("log")
    plt.xscale("log")

    axis_upper_limit = max(x + y)
    axis_lower_limit = min(x + y)

    colors = [int(l.partition("(")[0]) for l in x_labels]
    sizes = [c * 2 for c in colors]

    # Add some padding
    axis_lower_limit = axis_lower_limit * 0.8
    axis_upper_limit = axis_upper_limit * 1.2

    plt.xlim(axis_lower_limit, axis_upper_limit)
    plt.ylim(axis_lower_limit, axis_upper_limit)

    plt.xlabel("bdd runtime (ms)")
    plt.ylabel("dummiest runtime (ms)")
    plt.scatter(x, y, c=colors, s=sizes, cmap="winter")

    diagonal_x = numpy.linspace(axis_lower_limit, axis_upper_limit, 100)
    diagonal_y = diagonal_x

    plt.plot(diagonal_x, diagonal_y, color="black", linewidth=1)

    # mymodel = numpy.poly1d(numpy.polyfit(x, y, 2))
    # myline = numpy.linspace(min(x + y), max(x + y), 500)
    # plt.plot(myline, mymodel(myline), color="red")

    clb = plt.colorbar()
    clb.ax.set_title("Tree size")

    plt.tight_layout()
    plt.savefig(f"{output}.png")


if __name__ == "__main__":
    filename = "./benchmarking/algorithm_bdd_dummy.csv"
    output = Path(filename).stem
    output = (
        "plot_" + output[output.index("_") + 1 :]
    )  # get everything after the first _

    x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values = (
        read_results_from_csv(filename)
    )

    plot_results(x_labels, bdd_bu_values, dummiest_values, output)
