from functools import cmp_to_key
from typing import List

from sfldebug.tools.ranking_metrics import RankingMetrics
from sfldebug.tools.ranking_merge import RankMergeOperator
from sfldebug.tools.logger import logger
from sfldebug.tools.object import cmp_entities


def rank_entity(
    entity_analytics: dict,
    ranking_metrics: List[RankingMetrics],
    ranking_merge_op: RankMergeOperator
) -> float:
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
        logger.debug('Calculated ranking using metric "%s" is: %f.',
                     ranking_metric.name, entity_rank)
        rankings.append(entity_rank)

    logger.debug('Merging ranking using operator: "%s".',
                 ranking_merge_op.name)
    return ranking_merge_op(rankings)


def rank(
    entities_analytics: dict,
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

    entities_ranking = []
    for analytics in entities_analytics.values():
        entity_rank = rank_entity(analytics, ranking_metrics, ranking_merge_op)
        entities_ranking.append(
            {'entity_rank': entity_rank, 'properties': analytics['properties']})

    cmp_entity_rank = cmp_to_key(cmp_entities)
    entities_ranking.sort(key=cmp_entity_rank)
    logger.info('Entities ranking and sorting complete.')
    return entities_ranking
