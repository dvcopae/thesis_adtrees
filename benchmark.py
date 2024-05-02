from cProfile import label
import threading
import matplotlib.pyplot as plt

from bu import run as run_bu
from bilp import run as run_bilp

x = [6, 12, 18, 24, 30, 36]
dummiest = []
bilp_values = []


def eval_dummiest():
    for i in x:
        time_bu = run_bu("dummiest", f"./trees_w_assignments/thesis_tree_{i}.xml")
        dummiest.append(time_bu)


def eval_bilp():
    for i in x:
        time_bilp = run_bilp(f"./trees_w_assignments/thesis_tree_{i}.xml")
        bilp_values.append(time_bilp)


t1 = threading.Thread(target=eval_dummiest)
t2 = threading.Thread(target=eval_bilp)

t1.start()
t2.start()

t1.join()
t2.join()

plt.yscale("log")
plt.xlabel("Nodes")
plt.ylabel("ms")
plt.plot(x, dummiest, label="dummiest")
plt.plot(x, bilp_values, label="bilp")
plt.legend(loc="best")
plt.savefig("benchmark.png")
# plt.show()
