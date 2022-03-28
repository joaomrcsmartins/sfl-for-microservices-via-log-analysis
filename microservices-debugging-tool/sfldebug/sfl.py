from functools import cmp_to_key
from typing import Dict, List

from sfldebug.tools.ranking_metrics import RankingMetrics
from sfldebug.tools.ranking_merge import RankMergeOperator


def rank_entity(entity_analytics: dict, ranking_metrics: List[RankingMetrics],
                ranking_merge_op: RankMergeOperator) -> float:
    """Ranks a entity according to the metrics provided and returns the probability value.
    Requires also a ranking merge operator to merge the results of different metrics.
    If there is only one ranking metric to be applied, the ranking merge operator is ignored.

    Args:
        entity_analytics (dict): analytics of a entity, containing count of good and faulty
        executions and non-executions
        ranking_metrics (List[RankingMetrics]): list of ranking metrics to be applied to the entity
        analytics
        ranking_merge_op (RankMergeOperator): ranking merge operator to aggregate the metrics'
        rankings

    Returns:
        float: the ranking given to the entity, given its analytics
    """

    if len(ranking_metrics) == 1:
        return ranking_metrics[0](entity_analytics)

    rankings = []
    for ranking_metric in ranking_metrics:
        entity_rank = ranking_metric(entity_analytics)
        rankings.append(entity_rank)

    return ranking_merge_op(rankings)


def cmp_entities(ent1: Dict[str, float], ent2: Dict[str, float]) -> int:
    """Custom comparator for entities rankings, which contain only a single pair (key,value).
    The key is assumed to be of str type, and the value of float type

    Args:
        ent1 (Dict[str,float]): Entity ranking to be compared
        ent2 (Dict[str,float]): Other entity ranking to be compared

    Returns:
        int: 1 if ent1 has lower ranking or key higher, -1 if ent1 has higher ranking or key lower,
        0 if both ent are equal
    """
    key1, value1 = list(ent1.items())[0]
    key2, value2 = list(ent2.items())[0]

    if value1 < value2:
        return 1
    elif value1 > value2:
        return -1
    elif key1 > key2:
        return 1
    elif key1 < key2:
        return -1
    return 0


def rank(entities_analytics: dict, ranking_metrics: List[RankingMetrics],
         ranking_merge_op: RankMergeOperator = RankMergeOperator.AVG) -> List[dict]:
    """Ranks all the entities, according to the analytics and the ranking metrics provided.
    Requires also a ranking merge operator to merge the results of different metrics.
    Returns a list of dict, each containing the entity id (key) and resulting ranking.

    Args:
        entities_analytics (dict): analytics of a entity, containing count of good and faulty
        executions and non-executions
        ranking_metrics (List[RankingMetrics]): list of ranking metrics to be applied to the entity
        analytics
        ranking_merge_op (RankMergeOperator, optional): ranking merge operator to aggregate the
        metrics' rankings. Defaults to RankMergeOperator.AVG.

    Returns:
        List[dict]: list of rankings for each entity, sorted by rank in descending order
    """
    entities_ranking = []
    for key, analytics in entities_analytics.items():
        entity_rank = rank_entity(analytics, ranking_metrics, ranking_merge_op)
        entities_ranking.append({key: entity_rank})

    cmp_entity_rank = cmp_to_key(cmp_entities)
    entities_ranking.sort(key=cmp_entity_rank)
    return entities_ranking
