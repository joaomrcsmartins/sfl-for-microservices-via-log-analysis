from enum import Enum
import math
from typing import Tuple

from sfldebug.tools.logger import logger


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
    logger.debug('break entity: %s-"%s" EP-%d NP-%d EF-%d NF-%d',
                 entity_analytics['properties']['parent_name'],
                 entity_analytics['properties']['name'],
                 good_executed, good_passed, faulty_executed, faulty_passed)

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

    James A. Jones, Mary Jean Harrold, and John Stasko.
    2002. Visualization of test information to assist fault localization.
    In "Proceedings of the 24th International Conference on Software Engineering" (ICSE '02).
    Association for Computing Machinery, New York, NY, USA, 467-477.
    DOI: https://doi.org/10.1145/581339.581397

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

    M. Y. Chen, E. Kiciman, E. Fratkin, A. Fox and E. Brewer.
    "Pinpoint: problem determination in large, dynamic Internet services."
    Proceedings International Conference on Dependable Systems and Networks 2002, pp. 595-604.
    DOI: 10.1109/DSN.2002.1029005.

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

    Meyer, Andréia da Silva et al.
    Comparison of similarity coefficients used for cluster analysis with dominant markers in maize
    (Zea mays L).
    Genetics and Molecular Biology, 2004, v.27, n.1, pp. 83-91.
    DOI: https://doi.org/10.1590/S1415-47572004000100014>.

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

    R. Abreu, P. Zoeteweij and A. J. C. v. Gemund, "Localizing Software Faults Simultaneously."
    2009 Ninth International Conference on Quality Software, 2009, pp. 367-376.
    DOI: 10.1109/QSIC.2009.55.

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
    """O^p ranking metric. Works better for multiple-fault programs.

    Lee Naish, Hua Jie Lee, and Kotagiri Ramamohanarao.
    2011. A model for spectra-based software diagnosis.
    ACM Trans. Softw. Eng. Methodol. 20, 3, Article 11 (August 2011), 32 pages.
    DOI: https://doi.org/10.1145/2000791.2000795

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
    """O ranking metric. Optimal for single-fault programs.

    Lee Naish, Hua Jie Lee, and Kotagiri Ramamohanarao.
    2011. A model for spectra-based software diagnosis.
    ACM Trans. Softw. Eng. Methodol. 20, 3, Article 11 (August 2011), 32 pages.
    DOI: https://doi.org/10.1145/2000791.2000795

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

    L. Naish, H. J. Lee and K. Ramamohanarao, "Spectral Debugging with Weights and Incremental
    Ranking."
    2009 16th Asia-Pacific Software Engineering Conference, 2009, pp. 168-175.
    DOI: 10.1109/APSEC.2009.32.

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

    L. Naish, H. J. Lee and K. Ramamohanarao, "Spectral Debugging with Weights and Incremental
    Ranking."
    2009 16th Asia-Pacific Software Engineering Conference, 2009, pp. 168-175.
    DOI: 10.1109/APSEC.2009.32.

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
    Manipulate 'star_factor' to increase suspiciouness weight on executions in faulty cases.

    W. E. Wong, V. Debroy, Y. Li and R. Gao. "Software Fault Localization Using DStar (D*)."
    2012 IEEE Sixth International Conference on Software Security and Reliability, 2012, pp. 21-30.
    DOI: 10.1109/SERE.2012.12.

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

    Jian Xu, Zhenyu Zhang, W.K. Chan, T.H. Tse, Shanping Li.
    A general noise-reduction framework for fault localization of Java programs.
    Information and Software Technology, V.55, I.5, 2013, pp. 880-896.
    DOI: https://doi.org/10.1016/j.infsof.2012.08.006.

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

    def __call__(self, *args):
        return self.value(args)
