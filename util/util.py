import csv
import re
import secrets
import string
from operator import itemgetter


def remove_dominated_pts(actor, points):
    """
    Remove all dominated points (not better in both dimensions)
    """
    if not points:
        return []

    # If actor = 'a', sort first based on attack, and then on defense.
    # If actor = 'd', sort first based on defense, and then on attack.
    primary_index = 0 if actor == "d" else 1
    secondary_index = 1 - primary_index
    sorted_points = sorted(points, key=itemgetter(primary_index, secondary_index))

    pareto_front = [sorted_points[0]]
    for point in sorted_points[1:]:
        if point[0] > pareto_front[-1][0] and point[1] > pareto_front[-1][1]:
            pareto_front.append(point)

    return pareto_front


def remove_low_att_pts(actor, points):
    """
    Remove all points which have a lower attack cost for the same defense cost.
    Points must already have a minimum attack cost.
    """
    if not points:
        return []

    if actor == "a":
        index_to_compare, index_to_keep = 0, 1  # compare by defense, keep max attack
    else:
        index_to_compare, index_to_keep = 1, 0  # compare by attack, keep max defense

    cost_dict = {}
    for point in points:
        key = point[index_to_compare]
        value = point[index_to_keep]
        if key not in cost_dict or value > cost_dict[key]:
            cost_dict[key] = value

    if actor == "a":
        return [(k, v) for k, v in cost_dict.items()]
    else:
        return [(v, k) for k, v in cost_dict.items()]


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
