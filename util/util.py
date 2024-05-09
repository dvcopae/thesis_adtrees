from operator import itemgetter
import re


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
