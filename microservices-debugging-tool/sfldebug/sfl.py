from functools import cmp_to_key
from typing import List

from sfldebug.tools.ranking_metrics import RankingMetrics, normalize_rankings
from sfldebug.tools.ranking_merge import RankMergeOperator
from sfldebug.tools.logger import logger
from sfldebug.tools.object import cmp_entities


def rank_entities(
    entities_analytics: List[dict],
    ranking_metrics: List[RankingMetrics],
    ranking_merge_op: RankMergeOperator
) -> List[dict]:
    """Ranks entities using the metrics passed as arguments.
    For each metric, the rankings are calculated and then normalized, if needed.
    For each entity, the rankings are merged according to the operator passed as argument.
    Return a list of entities final rankings and its properties.

    Args:
        entities_analytics (List[dict]): list of analytics and properties for each entity
        ranking_metrics (List[RankingMetrics]): list of ranking metric to rank each entity
        ranking_merge_op (RankMergeOperator): operator to merge the rankings of each entity

    Returns:
        List[dict]: list of final rankings for each entity and its properties
    """
    metrics_rankings = dict(
        zip(ranking_metrics, [[] for i in ranking_metrics]))
    for metric in ranking_metrics:

        metric_rankings = [metric(entity)
                           for entity in entities_analytics]

        metric_rankings = normalize_rankings(metric_rankings, metric)

        metrics_rankings[metric] = metric_rankings

    logger.debug('Merging ranking using operator: "%s".',
                 ranking_merge_op.name)
    entities_rankings = []
    for index, entity_analytics in enumerate(entities_analytics):

        entity_rankings = [rank_list[index]
                           for rank_list in metrics_rankings.values()]

        entities_rankings.append(
            {'entity_rank': ranking_merge_op(entity_rankings),
             'properties': entity_analytics['properties']})

    return entities_rankings


def rank(
    entities_analytics: dict[str, dict],
    ranking_metrics: List[RankingMetrics],
    ranking_merge_op: RankMergeOperator = RankMergeOperator.AVG
) -> List[dict]:
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
    logger.info('Ranking entities using ranking metrics: %s.',
                [metric.name for metric in ranking_metrics])

    # unpack the values of each entity analytics into a list
    entities_analytics_unpacked = list(entities_analytics.values())

    entities_ranking = rank_entities(
        entities_analytics_unpacked, ranking_metrics, ranking_merge_op)

    cmp_entity_rank = cmp_to_key(cmp_entities)
    entities_ranking.sort(key=cmp_entity_rank)
    logger.info('Entities ranking and sorting complete.')
    return entities_ranking
