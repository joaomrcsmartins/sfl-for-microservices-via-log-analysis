from uuid import uuid4
from sfldebug.tools.logger import config_logging
from sfldebug.messages.receive import receive_mq
from sfldebug.tools.analytics import analyze_entities
from sfldebug.sfl import rank
from sfldebug.tools.ranking_metrics import RankingMetrics
from sfldebug.tools.ranking_merge import RankMergeOperator
from sfldebug.tools.writer import write_results_to_file

if __name__ == '__main__':
    # TODO command line arguments
    GOOD_ENTITIES_ID = 'logstash-output-good'
    FAULTY_ENTITIES_ID = 'logstash-output-bad'
    RANKING_METRICS = [RankingMetrics.MINUS]
    RANKING_MERGE_OPERATOR = RankMergeOperator.AVG

    EXECUTION_ID = str(uuid4())

    # configure logging for the execution
    config_logging(EXECUTION_ID)

    # receive logs and parse into entities
    entities = receive_mq(
        GOOD_ENTITIES_ID, FAULTY_ENTITIES_ID, EXECUTION_ID)

    # analyze entity statistics, hit spectra
    entities_analytics = analyze_entities(
        entities[GOOD_ENTITIES_ID], entities[FAULTY_ENTITIES_ID])

    # rank each entity according to the selected metrics
    entities_ranked = rank(
        entities_analytics, RANKING_METRICS, RANKING_MERGE_OPERATOR)
    write_results_to_file(entities_ranked, 'entities-ranking', EXECUTION_ID)
