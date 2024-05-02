import threading
import matplotlib.pyplot as plt

from bu import run as run_bu
from bilp import run as run_bilp, warmup_bilp

x = [6, 12, 18, 24, 30, 36]
x_labels = []
dummiest_values = []
bilp_values = []


def eval_dummiest():
    for i in x:
        time_bu, tree_size, def_size, att_size = run_bu(
            "dummiest", f"./trees_w_assignments/thesis_tree_{i}.xml"
        )
        x_labels.append(f"{tree_size}({def_size})")
        dummiest_values.append(time_bu)


def eval_bilp():
    warmup_bilp()
    for i in x:
        time_bilp, _, _, _ = run_bilp(f"./trees_w_assignments/thesis_tree_{i}.xml")
        bilp_values.append(time_bilp)


t1 = threading.Thread(target=eval_dummiest)
t2 = threading.Thread(target=eval_bilp)

t1.start()
t2.start()

t1.join()
t2.join()

plt.yscale("log")
plt.xlabel("Tree size(defenses)")
plt.xticks(x, x_labels)
plt.ylabel("ms")
plt.plot(x, bilp_values, linestyle="--", marker="o", label="bilp")
plt.plot(x, dummiest_values, linestyle="--", marker="o", label="dummiest")
plt.legend(loc="best")
plt.savefig("benchmark.png")

# plt.show()
