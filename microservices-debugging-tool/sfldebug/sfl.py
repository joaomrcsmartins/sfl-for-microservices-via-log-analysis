from functools import cmp_to_key
from typing import List

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


def cmp_entities(ent1: dict, ent2: dict) -> int:
    """Custom comparator for entities rankings.
    It is assumed the ranking is associated to key 'entity_rank'

    Args:
        ent1 (dict): Entity ranking to be compared
        ent2 (dict): Other entity ranking to be compared

    Returns:
        int: 1 if ent1 has lower ranking, -1 if ent1 has higher ranking,
        0 if both rankings are equal
    """
    rank1 = ent1['entity_rank']
    rank2 = ent2['entity_rank']

    if rank1 < rank2:
        return 1
    elif rank1 > rank2:
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
        List[dict]: list of entities ranked by fault location probability, in descending order
    """
    entities_ranking = []
    for analytics in entities_analytics.values():
        entity_rank = rank_entity(analytics, ranking_metrics, ranking_merge_op)
        entities_ranking.append(
            {'entity_rank': entity_rank, 'properties': analytics['properties']})

    cmp_entity_rank = cmp_to_key(cmp_entities)
    entities_ranking.sort(key=cmp_entity_rank)
    return entities_ranking
