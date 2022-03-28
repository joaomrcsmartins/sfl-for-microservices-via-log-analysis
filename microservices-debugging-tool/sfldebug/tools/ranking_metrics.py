from enum import Enum
import math
from typing import Tuple


def __break_entity_analytics(entity_analytics: dict) -> Tuple[int, int, int, int]:
    """Breaks known dict values and returns them in a tuple shape.

    Args:
        entity_analytics (dict): analytics of the entity in a dict

    Returns:
        Tuple[int, int, int, int]: the values of the dict returned in a tuple
    """
    # TODO fault tolerance /handling
    good_executed = entity_analytics['good_executed']
    good_passed = entity_analytics['good_passed']
    faulty_executed = entity_analytics['faulty_executed']
    faulty_passed = entity_analytics['faulty_passed']
    return good_executed, good_passed, faulty_executed, faulty_passed


def __executed_fraction(executed: int, not_executed: int) -> float:
    """Simple fraction calculation

    Args:
        executed (int): number of times an entity is executed
        not_executed (int): number of times an entity is not executed

    Returns:
        float: resultant fraction
    """
    return executed / (executed + not_executed)


def tarantula(entity_analytics: dict) -> float:
    """Tarantula ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, good_p, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)

    faulty_fraction = __executed_fraction(faulty_e, faulty_p)
    good_fraction = __executed_fraction(good_e, good_p)

    denominator = faulty_fraction + good_fraction

    return faulty_fraction / denominator


def jaccard(entity_analytics: dict) -> float:
    """Jaccard ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, _, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)

    denominator = faulty_e + faulty_p + good_e

    return faulty_e / denominator


def ochiai(entity_analytics: dict) -> float:
    """Ochiai ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, _, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)

    total_faulty = faulty_e + faulty_p
    total_executed = faulty_e + good_e

    denominator = math.sqrt(total_faulty*total_executed)

    return faulty_e / denominator


def zoltar(entity_analytics: dict) -> float:
    """Zoltar ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, _, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)

    exoneration_factor = 10000
    execution_factor = (faulty_p*good_e)/faulty_e

    denominator = faulty_e + faulty_p + \
        good_e + exoneration_factor*execution_factor

    return faulty_e / denominator


def op_metric(entity_analytics: dict) -> float:
    """O^p ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, good_p, faulty_e, _ = __break_entity_analytics(
        entity_analytics)

    denominator = good_e + good_p + 1

    fraction = faulty_e / denominator

    return faulty_e - fraction


def o_metric(entity_analytics: dict) -> float:
    """O ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, good_p, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)
    del good_e, faulty_e

    if faulty_p > 0:
        return -1
    return good_p


def kulczynksi2(entity_analytics: dict) -> float:
    """Kulczynski2 ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, _, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)

    faulty_fraction = __executed_fraction(faulty_e, faulty_p)
    faulty_executed_fraction = __executed_fraction(faulty_e, good_e)

    return 0.5 * (faulty_fraction + faulty_executed_fraction)


def mccon(entity_analytics: dict) -> float:
    """Mccon ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, _, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)

    numerator = math.pow(faulty_e, 2) - faulty_p*good_e

    total_faulty = faulty_e + faulty_p
    total_executed = faulty_e + good_e
    denominator = total_faulty * total_executed

    return numerator / denominator


def dstar(entity_analytics: dict) -> float:
    """Dstar (D*) ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, _, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)

    star_factor = 2
    numerator = star_factor * faulty_e
    denominator = faulty_p + good_e

    return numerator / denominator


def minus(entity_analytics: dict) -> float:
    """Minus ranking metric.
    See more in: TBA

    Args:
        entity_analytics (dict): analytics of the entity, when it is executed or not in good and
        faulty scenarios

    Returns:
        float: resulting ranking
    """
    good_e, good_p, faulty_e, faulty_p = __break_entity_analytics(
        entity_analytics)

    faulty_fraction = __executed_fraction(faulty_e, faulty_p)
    good_fraction = __executed_fraction(good_e, good_p)

    comp_faulty_fraction = 1 - faulty_fraction
    comp_good_fraction = 1 - good_fraction

    first_part = faulty_fraction / (faulty_fraction + good_fraction)

    second_part = comp_faulty_fraction / \
        (comp_faulty_fraction + comp_good_fraction)

    return first_part - second_part


class RankingMetrics(Enum):
    """Ranking metrics enum to easily access and add more ranking metrics.
    Each elem refers to the ranking metric function.
    """
    TARANTULA = tarantula
    JACCARD = jaccard
    OCHIAI = ochiai
    ZOLTAR = zoltar
    OP = op_metric
    O = o_metric
    KULCZYNSKI2 = kulczynksi2
    MCCON = mccon
    DSTAR = dstar
    MINUS = minus
