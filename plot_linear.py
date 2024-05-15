import csv

import matplotlib.pyplot as plt


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


def read_results_from_csv(file_path):
    x_labels = []
    dummiest_values = []
    bilp_values = []
    bdd_bu_values = []
    bdd_all_values = []
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            x_labels.append(row[0])
            if row[1] != "":
                dummiest_values.append(float(row[1]))

            if row[2] != "":
                bilp_values.append(float(row[2]))

            if row[3] != "":
                bdd_bu_values.append(float(row[3]))

            if row[4] != "":
                bdd_all_values.append(float(row[4]))

    return x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values


def plot_results(x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values):
    plt.figure(figsize=(16, 9))

    plt.yscale("log")
    plt.xlabel("Tree size(defenses)")
    plt.xticks(range(len(x_labels)), x_labels)
    # plt.xticks(rotation=90)
    plt.ylabel("Runtime (ms)")

    plot(range(min(len(x_labels), len(dummiest_values))), dummiest_values, "dummiest")
    plot(range(min(len(x_labels), len(bilp_values))), bilp_values, "bilp")
    plot(range(min(len(x_labels), len(bdd_bu_values))), bdd_bu_values, "bdd_bu")
    plot(range(min(len(x_labels), len(bdd_all_values))), bdd_all_values, "bdd_all")

    plt.legend(loc="best")
    plt.tight_layout()
    # plt.show()
    plt.savefig("benchmark.png")


if __name__ == "__main__":
    x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values = (
        read_results_from_csv("./benchmarks/algorithm_results_linear.csv")
    )
    plot_results(x_labels, dummiest_values, bilp_values, bdd_bu_values, bdd_all_values)
