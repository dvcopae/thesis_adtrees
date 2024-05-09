from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt

from adtrees.adtree import ADTree
from bu import run as run_bu
from bilp import run_average as run_bilp, warmup_bilp
from bdd import run_average as run_bdd

x = [6, 12, 18, 24, 30, 36, 42, 48, 54]
dummy_x = [i for i in x if i <= 36]
x_labels = []
dummiest_values = []
bilp_values = []
bdd_values = []


def eval_dummiest(i):
    time_bu = run_bu("dummiest", f"./trees_w_assignments/tree_{i}.xml")
    print(f"Dummiest - finished {i}")
    return time_bu


def eval_bilp(i):
    time = run_bilp(f"./trees_w_assignments/tree_{i}.xml", 2)
    print(f"BILP - finished {i}")
    return round(time * 1000, 2)


def eval_bdd(i):
    time = run_bdd(f"./trees_w_assignments/tree_{i}.xml", 50)
    print(f"BDD - finished {i}")
    return round(time * 1000, 2)


if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        # Collect dummiest values and x_labels using parallel execution
        dummiest_values = list(executor.map(eval_dummiest, dummy_x))

        # Collect bilp values
        bilp_values = list(executor.map(eval_bilp, x))

        # Collect bdd values
        bdd_values = list(executor.map(eval_bdd, x))

    for i in x:
        T = ADTree(f"./trees_w_assignments/tree_{i}.xml")
        tree_size = T.subtree_size()
        defense_count = len(T.get_basic_actions("d"))
        x_labels.append(f"{tree_size}({defense_count})")

    print(x_labels)

    plt.yscale("log")
    plt.xlabel("Tree size(defenses)")
    plt.xticks(x, x_labels)
    plt.ylabel("Runtime (ms)")
    plt.plot(dummy_x, dummiest_values, linestyle="--", marker="o", label="dummiest")
    plt.plot(x, bilp_values, linestyle="--", marker="o", label="bilp")
    plt.plot(x, bdd_values, linestyle="--", marker="o", label="bdd")

    # Annotate bilp values on the plot
    for i, txt in enumerate(bilp_values):
        plt.annotate(txt, (x[i], round(bilp_values[i], 1)))

    # Annotate dummiest values on the plot
    for i, txt in enumerate(dummiest_values):
        plt.annotate(txt, (x[i], round(dummiest_values[i], 1)))

    # Annotate dummiest values on the plot
    for i, txt in enumerate(bdd_values):
        plt.annotate(txt, (x[i], round(bdd_values[i], 1)))

    plt.legend(loc="best")
    plt.savefig("benchmark.png")
