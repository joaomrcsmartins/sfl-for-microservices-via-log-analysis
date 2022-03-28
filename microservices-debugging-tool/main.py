import sfldebug.messages.receive as message_receive
import sfldebug.tools.analytics as a
import sfldebug.sfl as sfl
from sfldebug.tools.ranking_metrics import RankingMetrics
from sfldebug.tools.writer import write_json_to_file

if __name__ == '__main__':
    # TODO once messages are not received in MQ, add following steps
    GOOD_ENTITIES_ID = 'logstash-output-good'
    FAULTY_ENTITIES_ID = 'logstash-output-faulty'
    entities = message_receive.receive_mq(GOOD_ENTITIES_ID, FAULTY_ENTITIES_ID)
    entities_analytics = a.analyze_entities(
        entities[GOOD_ENTITIES_ID], entities[FAULTY_ENTITIES_ID])
    entities_ranked = sfl.rank(
        entities_analytics, [RankingMetrics.OCHIAI, RankingMetrics.JACCARD])
    write_json_to_file(entities_ranked, 'entities-ranking')
