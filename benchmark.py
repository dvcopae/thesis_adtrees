from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt

from bu import run as run_bu
from bilp import run as run_bilp, warmup_bilp

x = [6, 12, 18, 24, 30, 36]
x_labels = []
dummiest_values = []
bilp_values = []


def eval_dummiest(i):
    time_bu, tree_size, def_size, att_size = run_bu(
        "dummiest", f"./trees_w_assignments/thesis_tree_{i}.xml"
    )
    return f"{tree_size}({def_size})", time_bu


def eval_bilp(i):
    time_bilp, _, _, _ = run_bilp(f"./trees_w_assignments/thesis_tree_{i}.xml")
    return time_bilp


if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        warmup_bilp()

        # Collect dummiest values and x_labels using parallel execution
        results = executor.map(eval_dummiest, x)
        for label, value in results:
            x_labels.append(label)
            dummiest_values.append(value)

        # Collect bilp values using parallel execution
        bilp_values.extend(executor.map(eval_bilp, x))

    plt.yscale("log")
    plt.xlabel("Tree size(defenses)")
    plt.xticks(x, x_labels)
    plt.ylabel("Runtime (ms)")
    plt.plot(x, bilp_values, linestyle="--", marker="o", label="bilp")
    plt.plot(x, dummiest_values, linestyle="--", marker="o", label="dummiest")

    # Annotate bilp values on the plot
    for i, txt in enumerate(bilp_values):
        plt.annotate(txt, (x[i], round(bilp_values[i], 1)))

    # Annotate dummiest values on the plot
    for i, txt in enumerate(dummiest_values):
        plt.annotate(txt, (x[i], round(dummiest_values[i], 1)))

    plt.legend(loc="best")
    plt.savefig("benchmark.png")
