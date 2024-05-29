from __future__ import annotations

import csv
import re
import secrets
import string
from operator import itemgetter


def remove_dominated_pts(points):
    """
    Remove all dominated points (not better in both dimensions)
    """
    if not points:
        return []

    # If actor = 'd', sort first based on defense, and then on attack.
    sorted_points = sorted(points, key=itemgetter(0, 1))

    pareto_front = [sorted_points[0]]

    for point in sorted_points[1:]:
        # We have two conditions:
        # 1) The defense cost of point > defense cost of the last element from pareto_front
        # 2) The attack cost of point > attack cost of the last element from pareto_front

        if point[0] > pareto_front[-1][0] and point[1] > pareto_front[-1][1]:
            pareto_front.append(point)

    return pareto_front


def remove_low_att_pts(points):
    """
    ATTACKER'S VIEW - Remove all points which have a lower attack cost for the same defense cost.
    """
    if not points:
        return []

    cost_dict = {}
    for point in points:
        def_cost = point[0]
        att_cost = point[1]
        if def_cost not in cost_dict or att_cost > cost_dict[def_cost]:
            cost_dict[def_cost] = att_cost

    return list(cost_dict.items())


def clean_tla_identifier(identifier):
    """
    Clean and convert a string to a valid TLA+ identifier.
    """
    # Remove all non-alphanumeric characters and underscores
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", identifier)

    # If the cleaned string starts with a digit, prefix with an underscore
    if cleaned and cleaned[0].isdigit():
        cleaned = "_" + cleaned

    return cleaned


def generate_random_string(length=10):
    # Generate a random string of fixed length
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def read_results_from_csv(file_path):
    x_labels = []
    dummiest_values = []
    bilp_values = []
    bdd_bu_values = []
    bdd_all_def_values = []
    bu_values = []
    with open(file_path, encoding="utf-8") as file:
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
                bdd_all_def_values.append(float(row[4]))

            if row[5] != "":
                bu_values.append(float(row[5]))

    return (
        x_labels,
        dummiest_values,
        bilp_values,
        bdd_bu_values,
        bdd_all_def_values,
        bu_values,
    )
