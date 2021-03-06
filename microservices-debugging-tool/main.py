# pylint: disable=broad-except,dangerous-default-value
from typing import Callable, List, Optional
from uuid import uuid4

import sfldebug.tools.logger as sfl_logger
from sfldebug.messages.receive import receive_mq
from sfldebug.analytics import analyze_entities
from sfldebug.sfl import rank
from sfldebug.tools.ranking_metrics import RankingMetrics
from sfldebug.tools.ranking_merge import RankMergeOperator
from sfldebug.tools.writer import write_results_to_file
from sfldebug.tools.logger import logger


def run(
    execution_id: str,
    good_entities_id: str,
    faulty_entities_id: str,
    receiver_method: Callable[[str, str, str], dict],
    rankings_metrics: List[RankingMetrics] = [RankingMetrics.OCHIAI],
    ranking_merge_operator: RankMergeOperator = RankMergeOperator.AVG
) -> Optional[List[dict]]:
    """Runs the microservices debugging tool.

    Uses the good and faulty entities id to set up MQ communication channels and starts receiving
    messages. When a processed log is received, it is parsed into an Entity object. Once the
    communication is finished, a keyboard interruption is used to shutdown the channels (CTRL+C).

    The processed entities are then refined and merged, ready for analysis. That analysis consists
    of tracking the executions and not executions of each entity for each request and store those
    analytics to be ranked.

    The ranking is obtained applying the specified metrics to each entity' analytics. The ranking
    are normalized if need be, and then merged into a final ranking. The list of ranked entities
    is sorted by highest ranking and returned.

    Each entity ranking contains identification of the entity and also its properties and
    references. Its possible to check in each ranked entity the occurrences and the log
    information that are associated to it.

    Args:
        execution_id (str): a unique id to be used while logging and storing results.
        good_entities_id (str): the name of the exchange to receive logs from good executions.
        faulty_entities_id (str): the name of the exchange to receive logs from faulty executions.
        receiver_method (Callable[[str, str, str], dict]): method to receive log messages and parse
        entities. Must receive three arguments, two strings for good and faulty entities ids, and a
        third for the execution id. The return value must be a dict with two pairs key-value. The
        keys for the object must be the good and faulty entities id, and the values must be the
        sets of parsed entities, objects of class sfldebug.entity.Entity.
        rankings_metrics (List[RankingMetrics], optional): the list of metrics used to rank the
        entities processed from the logs. Defaults to [RankingMetrics.OCHIAI].
        ranking_merge_operator (RankMergeOperator, optional): the operator used to merge the
        rankings from different metrics. Defaults to RankMergeOperator.AVG.

    Returns:
        Optional[List[dict]]: the list of ranked entities with their properties and references.
        If there are errors while executing, returns None.
    """
    successful_run = False
    entities_ranked: Optional[List[dict]] = None
    try:
        # configure logging for the execution
        sfl_logger.config_logger(execution_id)

        # receive logs and parse into entities
        entities = receiver_method(
            good_entities_id, faulty_entities_id, execution_id)

        # analyze entity statistics, hit spectra
        entities_analytics = analyze_entities(
            entities[good_entities_id], entities[faulty_entities_id])

        # rank each entity according to the selected metrics
        entities_ranked = rank(
            entities_analytics, rankings_metrics, ranking_merge_operator)

        # write entity references separately for further inspection, if needed
        entities_with_references = [entity['properties']
                                    for entity in entities_ranked]
        write_results_to_file(entities_with_references,
                              'entities-references', execution_id)

        # remove references from the rank to alleviate
        for entity in entities_ranked:
            del entity['properties']['references']

        write_results_to_file(
            entities_ranked, 'entities-ranking', execution_id)
        successful_run = True
    except Exception as err:
        logger.exception(err)
    finally:
        if successful_run:
            logger.info('Succesfully executed, terminating.')
        else:
            logger.fatal('Errors occured, shutting down.')
        sfl_logger.clean_handlers()
    return entities_ranked


if __name__ == '__main__':
    # TODO command line arguments
    GOOD_ENTITIES_ID = 'logstash-output-good'
    FAULTY_ENTITIES_ID = 'logstash-output-bad'
    RANKING_METRICS = [RankingMetrics.OCHIAI, RankingMetrics.JACCARD]
    RANKING_MERGE_OPERATOR = RankMergeOperator.AVG

    EXECUTION_ID = str(uuid4())

    run(EXECUTION_ID, GOOD_ENTITIES_ID, FAULTY_ENTITIES_ID, receive_mq,
        RANKING_METRICS, RANKING_MERGE_OPERATOR)
