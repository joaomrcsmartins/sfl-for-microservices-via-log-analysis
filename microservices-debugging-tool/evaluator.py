import os
from multiprocessing import Pool
import time
from functools import cmp_to_key
from uuid import uuid4
from typing import List, Optional
import logging
import json
import pika

from main import run
from sfldebug.tools.ranking_metrics import RankingMetrics
from sfldebug.tools.ranking_merge import RankMergeOperator
from sfldebug.tools.object import cmp_deltas
from sfldebug.tools.writer import write_results_to_file

GOOD_LOGS_PATH = 'good_logs_path'
FAULTY_LOGS_PATH = 'faulty_logs_path'
GOOD_LOGS_EXCHANGE = 'good_logs_exchange'
FAULTY_LOGS_EXCHANGE = 'faulty_logs_exchange'
FAULTY_ENTITIES = 'faulty_entities'
SCENARIO_KEYS = [GOOD_LOGS_PATH, FAULTY_LOGS_PATH, FAULTY_ENTITIES]
LOG_PROCESSING_TIMEOUT_SECONDS = 4
DEFAULT_PARENT_ENTITY_WEIGHT = 0.4


def get_scenario(sc_filepath: str) -> dict:
    """Open the file and read the scenario contents in JSON format.
    Each file should contain 3 attributes/keys. One for the good logs file path.
    Another for the bad logs file path. And a third for the list of faulty entities expected to be
    found during the execution of the scenario.

    Args:
        sc_filepath (str): the file path with the scenario contents

    Raises:
        AttributeError: If any of the required attributes is missing, an exception is raised

    Returns:
        dict: return the read scenario in a python object
    """
    with open(sc_filepath, 'r', encoding='utf-8') as scenario_file:
        scenario: dict = json.load(scenario_file)

        # check if any of the required attributes is None
        if any(key not in scenario.keys() for key in SCENARIO_KEYS):
            raise AttributeError(
                'Scenario in "{}" misses at least one of the scenario keys.'.format(sc_filepath))
        return scenario


def launch_scenario(scenario: dict) -> None:
    """From a proper scenario, open the log files of good and bad executions, and sends them
    through a MQ channel to the log processor tool, which also expects the logs in a MQ.
    Two exchanges are used, one for good logs and one for bad logs.
    Once the logs are sent, a period of LOG_PROCESSING_TIMEOUT_SECONDS is waited before sending
    a shutdown signal to the debugging tool communication, signaling that no more messages will be
    sent.
    After sending the shutdown signal the connection is closed.

    Args:
        scenario (dict): scenario object containing the file paths of the good and bad logs.
    """

    good_logs_path = scenario[GOOD_LOGS_PATH]
    faulty_logs_path = scenario[FAULTY_LOGS_PATH]
    good_logs_exchange = scenario[GOOD_LOGS_EXCHANGE]
    faulty_logs_exchange = scenario[FAULTY_LOGS_EXCHANGE]

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=good_logs_exchange, durable=True)
    with open(os.path.abspath(good_logs_path), 'r', encoding='utf-8') as log_file:

        for log in log_file:
            channel.basic_publish(
                exchange=good_logs_exchange, routing_key=good_logs_exchange, body=log)

    channel.exchange_declare(exchange=faulty_logs_exchange, durable=True)
    with open(os.path.abspath(faulty_logs_path), 'r', encoding='utf-8') as log_file:

        for log in log_file:
            channel.basic_publish(exchange=faulty_logs_exchange,
                                  routing_key=faulty_logs_exchange, body=log)
    # wait for log processing
    time.sleep(LOG_PROCESSING_TIMEOUT_SECONDS)
    print('Sending channel shutdown signals.')
    channel.exchange_declare(exchange='channel-stop', durable=True)
    channel.basic_publish(exchange='channel-stop', routing_key='', body='')
    channel.basic_publish(exchange='channel-stop', routing_key='', body='')
    connection.close()


def evaluate_scenario(
    ranked_entities: Optional[List[dict]],
    scenario: dict
) -> dict:
    """Evaluate a particular scenario by analyzing the position of the faulty entities in the
    tool's ranking. For each entity the accuracy of its given ranking is calculated.
    The tool's total accuracy is determined and the evaluation results are shown in the console and
    the compiled evaluation results are returned.

    Args:
        ranked_entities (Optional[List[dict]]): the ranked entities provided by the tool.
        scenario (dict): the scenario object containing the list of faulty entities already known.

    Raises:
        RuntimeError: Is the ranked list is empty or missing, raises an exception.

    Returns:
        dict: scenario evaluation results
    """
    if ranked_entities is None or len(ranked_entities) == 0:
        raise RuntimeError

    faulty_entities: List[dict] = scenario[FAULTY_ENTITIES]
    total_faulty_entities = len(faulty_entities)

    total_ranked_entities = len(ranked_entities)
    evaluated_entities = evaluate_ranked_entities(
        ranked_entities, faulty_entities, total_ranked_entities)

    scenario_evaluation = {'evaluated_entities': [],
                           'total_scenario_accuracy': 0}
    for i, eval_entity in enumerate(evaluated_entities):
        delta_entity = eval_entity['delta_entity'] - i
        delta_parent_entity = eval_entity['delta_parent_entity'] - i
        eval_accuracy = calculate_ranking_accuracy(
            delta_entity, delta_parent_entity, total_faulty_entities, total_ranked_entities,
            parent_weight=1/total_ranked_entities)
        scenario_evaluation['total_scenario_accuracy'] += eval_accuracy
        total_ranked_entities -= 1

        # register entity accuracy evaluation
        scenario_evaluation['evaluated_entities'].append(
            {
                'name': eval_entity['name'],
                'ranking_value': eval_entity['ranking_entity'],
                'ranking_position': delta_entity + i + 1,
                'accuracy': eval_accuracy * total_faulty_entities,
                'global_accuracy': eval_accuracy
            })
        print(('Entity "{}" was ranked in {} place, with value {:.5f},'
               ' and it has {:.3%} accuracy. Contributes with {:.3%} to total accuracy').format(
                   eval_entity['name'], delta_entity +
            i + 1, eval_entity['ranking_entity'], eval_accuracy *
            total_faulty_entities, eval_accuracy
        ))

    print('This scenario total accuracy was {:.3%}.'.format(
        scenario_evaluation['total_scenario_accuracy']))

    return scenario_evaluation


def evaluate_ranked_entities(
    ranked_entities: List[dict],
    faulty_entities: List[dict],
    total_ranked_entities: int
) -> List[dict]:
    """Evaluate ranked entities by determining the distance of the entity rank to the top.
    Evaluates also the parent entity rank.
    The result is sorted according to the entity delta, in ascending order.

    Args:
        ranked_entities (Optional[List[dict]]): list of ranked entities
        faulty_entities (List[dict]): list of faulty entities to be evaluated by rankings
        total_ranked_entities (int): number of ranked entities to be evaluated. Aka,
        len(ranked_entities).

    Returns:
        List[dict]: list of faulty entities evaluated and sorted
    """
    entities_evaluated: List[dict] = []
    for entity in faulty_entities:
        entity_name = entity['name']
        entity_parent = entity['parent']

        delta_entity = total_ranked_entities
        ranking_entity = 0
        delta_parent_entity = total_ranked_entities
        ranking_parent_entity = 0
        for i, ranked_entity in enumerate(ranked_entities):
            if ranked_entity['properties']['name'] == entity_name:
                delta_entity = i
                ranking_entity = ranked_entity['entity_rank']
            elif ranked_entity['properties']['name'] == entity_parent:
                delta_parent_entity = i
                ranking_parent_entity = ranked_entity['entity_rank']
            if delta_entity < total_ranked_entities and delta_parent_entity < total_ranked_entities:
                break

        entity_evaluated = entity.copy()
        entity_evaluated['delta_entity'] = delta_entity
        entity_evaluated['delta_parent_entity'] = delta_parent_entity
        entity_evaluated['ranking_entity'] = ranking_entity
        entity_evaluated['ranking_parent_entity'] = ranking_parent_entity
        entities_evaluated.append(entity_evaluated)

    cmp_entity_rank = cmp_to_key(cmp_deltas)
    entities_evaluated.sort(key=cmp_entity_rank)
    return entities_evaluated


def calculate_ranking_accuracy(
    delta_entity: int,
    delta_parent_entity: int,
    total_faulty_entities: int,
    total_ranked_entities: int,
    parent_weight: float = DEFAULT_PARENT_ENTITY_WEIGHT
) -> float:
    """Calculates the entity accuracy and returns the value.
    The final entity accuracy is the total entity accuracy divided by the total of faulty entities
    (to evaluate).
    The total entity accuracy is the sum of the entity accuracy and its parent accuracy (weighted)
    The entity accuracy is obtained by the distance of the entity ranking to the top
    (1 - delta/total).
    The parent accuracy has the same formula (considering its delta), as parent entities are part
    of the rank too.
    The weighted parent accuracy is a mechanism to keep the influence of parent rankings in check,
    since they are more general components of the system and do not provide a fine-grained location
    of the fault.

    Args:
        delta_entity (int): the delta of the entity ranking
        delta_parent_entity (int): the delta of the parent entity ranking
        total_faulty_entities (int): total number of faulty entities to be evaluated
        total_ranked_entities (int): total number of entities in the ranking
        parent_weight (float, optional): Weight to tone down the influence of the parent ranking.
        Defaults to DEFAULT_PARENT_ENTITY_WEIGHT.

    Returns:
        float: the final entity accuracy
    """
    entity_accuracy = 1 - (delta_entity / total_ranked_entities)
    parent_accuracy = 1 - (delta_parent_entity / total_ranked_entities)
    weighted_parent_accuracy = parent_weight * parent_accuracy
    total_entity_accuracy = min(
        entity_accuracy + weighted_parent_accuracy, 1.0)
    return float(format(total_entity_accuracy / total_faulty_entities, '.5f'))


def run_evaluator(scenarios_dir_name: str) -> None:
    """Run the tool evaluator by setting up and execution the scenarios saved inside the folder
    passed as argument.
    For each file inside the folder, reads the contents and sets up the scenario.
    The logs found in each scenario are sent to the log processor tool that must be running.
    Once the debugging tool returns the results, they are evaluated according to the method
    specified in evaluate_scenario.
    The results of each scenario are saved to a file and printed on the console.

    Args:
        scenarios_dir_name (str): name of the folder where the scenarios are stored
    """
    good_entities_id = 'logstash-output-good'
    faulty_entities_id = 'logstash-output-bad'
    ranking_metrics = [RankingMetrics.OCHIAI, RankingMetrics.JACCARD]
    ranking_merge_operator = RankMergeOperator.AVG
    scenarios_dir = os.path.join(os.getcwd(), scenarios_dir_name)
    for filename in os.listdir(scenarios_dir):
        try:
            current_scenario = get_scenario(
                os.path.join(scenarios_dir, filename))
            execution_id = str(uuid4())
            with Pool(1) as pool:
                pool.apply_async(
                    launch_scenario, kwds={'scenario': current_scenario})
                entities_rankings = run(execution_id, good_entities_id, faulty_entities_id,
                                        ranking_metrics, ranking_merge_operator)
                evaluation_results = evaluate_scenario(
                    entities_rankings, current_scenario)
                write_results_to_file(evaluation_results,
                                      filename+'.evaluation', execution_id)
        except AttributeError as err:
            logging.exception(err)
        except RuntimeError:
            logging.exception(RuntimeError(
                'Failed run in scenario of "{}"'.format(filename)))
        except ValueError as err:
            logging.exception(err)


if __name__ == '__main__':
    run_evaluator('test_scenarios')
