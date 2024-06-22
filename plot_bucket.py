from __future__ import annotations

import statistics
from collections import defaultdict

import matplotlib.pyplot as plt

from run_benchmark import save_results_to_csv
from utils.util import read_results_from_csv


def plot_data(x, y, name):
    plt.plot(x, y, label=name)


def bucket_values(nodes, time, n):
    global TOTAL_NODES
    paired_values = list(zip(nodes, time))
    # sort increasing on x
    paired_values.sort(key=lambda x: x[0])

    buckets = defaultdict(list)

    for x, y in paired_values:
        bucket_key = (x // n) * n
        buckets[bucket_key].append(y)

    # if there are not at least ... examples, the median might be wrong
    for k in list(buckets.keys()):
        if len(buckets[k]) < 5:
            del buckets[k]

    # calculate the medians in seconds
    medians = {
        bucket: round(statistics.median(values) / 1000, 4)
        for bucket, values in buckets.items()
    }

    for k, v in buckets.items():
        print(
            f"Bucket: {k}, items: {len(v)}, max: {round(max(v)/1000, 4)}, median: {medians[k]}",
        )

    print()
    return list(medians.keys()), list(medians.values())


def parse_label(l):
    return int(l.split("(")[0])


def get_dummy_data():
    naive_x = []
    naive_y = []

    i, dummy_v, _, _, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_dummiest_bdd-bu.csv",
    )
    naive_x.extend(i)
    naive_y.extend(dummy_v)

    i, dummy_v, _, _, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_dummiest_bilp.csv",
    )
    naive_x.extend(i)
    naive_y.extend(dummy_v)

    i, dummy_v, _, _, _, _, _
    read_results_from_csv("./benchmarking/algorithm_dummiest_bu.csv")
    naive_x.extend(i)
    naive_y.extend(dummy_v)

    naive_x = [parse_label(l) for l in naive_x]

    return naive_x, naive_y


def get_bilp_data():
    bilp_x = []
    bilp_y = []

    i, _, bilp_v, _, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_dummiest_bilp.csv",
    )
    bilp_x.extend(i)
    bilp_y.extend(bilp_v)

    i, _, bilp_v, _, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_bu_bilp.csv",
    )
    bilp_x.extend(i)
    bilp_y.extend(bilp_v)

    i, _, bilp_v, _, _, _, _
    read_results_from_csv("./benchmarking/algorithm_bdd-bu_bilp.csv")
    bilp_x.extend(i)
    bilp_y.extend(bilp_v)

    bilp_x = [parse_label(l) for l in bilp_x]

    return bilp_x, bilp_y


def get_bu_data():
    bu_x = []
    bu_y = []

    i, _, _, _, _, bu_v, _ = read_results_from_csv(
        "./benchmarking/algorithm_dummiest_bu.csv",
    )
    bu_x.extend(i)
    bu_y.extend(bu_v)

    i, _, _, _, _, bu_v, _ = read_results_from_csv(
        "./benchmarking/algorithm_bu_bilp.csv",
    )
    bu_x.extend(i)
    bu_y.extend(bu_v)

    i, _, _, _, _, bu_v, _ = read_results_from_csv(
        "./benchmarking/algorithm_bu_bdd-bu.csv",
    )
    bu_x.extend(i)
    bu_y.extend(bu_v)

    bu_x = [parse_label(l) for l in bu_x]

    return bu_x, bu_y


def get_bdd_bu_data():
    bdd_bu_x = []
    bdd_bu_y = []

    i, _, _, bdd_bu_v, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_bdd-bu_bdd-all-def.csv",
    )
    bdd_bu_x.extend(i)
    bdd_bu_y.extend(bdd_bu_v)

    i, _, _, bdd_bu_v, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_bdd-bu_bdd-paths.csv",
    )
    bdd_bu_x.extend(i)
    bdd_bu_y.extend(bdd_bu_v)

    i, _, _, bdd_bu_v, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_bdd-bu_bilp.csv",
    )
    bdd_bu_x.extend(i)
    bdd_bu_y.extend(bdd_bu_v)

    i, _, _, bdd_bu_v, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_bu_bdd-bu.csv",
    )
    bdd_bu_x.extend(i)
    bdd_bu_y.extend(bdd_bu_v)

    i, _, _, bdd_bu_v, _, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_dummiest_bdd-bu.csv",
    )
    bdd_bu_x.extend(i)
    bdd_bu_y.extend(bdd_bu_v)

    bdd_bu_x = [parse_label(l) for l in bdd_bu_x]

    return bdd_bu_x, bdd_bu_y


def get_bdd_paths_data():
    bdd_paths_x = []
    bdd_paths_y = []

    i, _, _, _, _, _, bdd_paths_v = read_results_from_csv(
        "./benchmarking/algorithm_bdd-bu_bdd-paths.csv",
    )
    bdd_paths_x.extend(i)
    bdd_paths_y.extend(bdd_paths_v)

    i, _, _, _, _, _, bdd_paths_v = read_results_from_csv(
        "./benchmarking/algorithm_bdd-paths_bdd-all-def.csv",
    )
    bdd_paths_x.extend(i)
    bdd_paths_y.extend(bdd_paths_v)

    bdd_paths_x = [parse_label(l) for l in bdd_paths_x]

    return bdd_paths_x, bdd_paths_y


def get_bdd_def_data():
    bdd_def_x = []
    bdd_def_y = []

    i, _, _, _, bdd_def_v, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_bdd-bu_bdd-all-def.csv",
    )
    bdd_def_x.extend(i)
    bdd_def_y.extend(bdd_def_v)

    i, _, _, _, bdd_def_v, _, _ = read_results_from_csv(
        "./benchmarking/algorithm_bdd-paths_bdd-all-def.csv",
    )
    bdd_def_x.extend(i)
    bdd_def_y.extend(bdd_def_v)

    bdd_def_x = [parse_label(l) for l in bdd_def_x]

    return bdd_def_x, bdd_def_y


lower_limit = 10**-4.5
upper_limit = 10**4
plt.figure(figsize=(10, 6))
plt.yscale("log")
plt.xlabel("Tree size")
plt.ylabel("Time (s)")
# plt.xscale("log", base=2)
plt.grid(color="lightgray", linestyle="-", linewidth=0.05)
plt.ylim(lower_limit, upper_limit)

N = 20

print("BU")
bu_x, bu_y = get_bu_data()
bu_x, bu_y = bucket_values(bu_x, bu_y, N)
plt.plot(bu_x, bu_y, linestyle="--", marker="o", label="BU")

print("NAIVE")
naive_x, naive_y = get_dummy_data()
naive_x, naive_y = bucket_values(naive_x, naive_y, N)
plt.plot(naive_x, naive_y, linestyle="--", marker="o", label="Naive")

print("BILP")
bilp_x, bilp_y = get_bilp_data()
bilp_x, bilp_y = bucket_values(bilp_x, bilp_y, N)
plt.plot(bilp_x, bilp_y, linestyle="--", marker="o", label="BILP")

print("BDD_PATHS")
bdd_paths_x, bdd_paths_y = get_bdd_paths_data()
bdd_paths_x, bdd_paths_y = bucket_values(bdd_paths_x, bdd_paths_y, N)
plt.plot(bdd_paths_x, bdd_paths_y, linestyle="--", marker="o", label="BDD_PATHS")

print("BDD_ALL_DEF")
bdd_def_x, bdd_def_y = get_bdd_def_data()
bdd_def_x, bdd_def_y = bucket_values(bdd_def_x, bdd_def_y, N)
plt.plot(bdd_def_x, bdd_def_y, linestyle="--", marker="o", label="BDD_ALL_DEF")

print("BDD_BU")
bdd_bu_x, bdd_bu_y = get_bdd_bu_data()
bdd_bu_x, bdd_bu_y = bucket_values(bdd_bu_x, bdd_bu_y, N)
plt.plot(bdd_bu_x, bdd_bu_y, linestyle="--", marker="o", label="BDD_BU")

plt.legend(loc="best")
plt.tight_layout()
plt.savefig("bucket.pdf")

save_results_to_csv(
    bdd_bu_x,
    naive_y,
    bilp_y,
    bdd_bu_y,
    bdd_def_y,
    bu_y,
    bdd_paths_y,
    name="algorithm_bucket",
)
