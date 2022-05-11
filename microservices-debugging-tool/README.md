# Microservices Debugging Tool

The microservices debugging tool works by applying the known SFL technique on the information extraction from logs produced by microservices.

Once the logs have been processed by the log processor tool, they are sent to be collected.
This tool sets up communication to start receiving them with message queues.
They required to be separated into two different sets of logs, one belonging to correct executions of the microservices and the other belonging to faulty executions of the microservices.

By each log received, the log data is parsed into a entity object, which is the fundamental element of SFL.
In this approach, two types of entities are currently created, with different granularity. One is the Service Entity, which represents the (micro)service.
The represents the Method Entity, created when the log contains relevant data about the invoked method. Since log uniformity is not assumed or always feasible,
the tool accepts the two levels of granularity and ranks the two types together.

After receiving all the data, the communication is shutdown (manually with CTRL+C, or by sending stop messages to the channels) and collected entities are merged into unique entities with their references.

The analysis is the first part of the SFL techniques, which tracks the *hit spectra*, i.e., when an entity is executed or not in each unique request (execution).

Once that is complete, the ranking of the entities takes place, by applying one or more metrics currently available, and merging them using a common operator (mean or median at this moment).
Finally the ranked entities are sorted and the final result saved into a JSON file to be analyzed by the developer.

The tool also provides logging of the execution so that in each run the user can look into the steps of the tool and each component is properly documented.

## Prerequisites

* Python 3.X
* Pip
* [Microservices Log Processor](../microservices-log-processor/) set up and running outputting logs to both channels **logstash-output-good** and **logstash-output-bad**

## Installation and setup

1. Install Pipenv: ```pip install --user pipenv```
2. Install dependencies: ```pipenv install```

## Running the application

1. You can activate the virtual environment with pipenv: ```pipenv shell```
   1. And inside start the application: ```python main.py```

2. Or instead, simply execute: ```pipenv run python main.py```
3. To stop message receiving press CTRL+C or use the same MQ channel and send a message (content is irrelevant) to the exchange **'channel-stop'** (two messages in total, one for the good logs channel, and another for the bad logs channel)
4. After that the processing and ranking is completed and the logs are stored in **/logs** and the rankings and other results are stored in **/results**

## Running the evaluator

The evaluator is a helper tool to evaluate the accuracy of the SFL debugging tool. From a scenario specified in a JSON file inside **/test_scenarios** it sends logs to the tool, receives the ranking and evaluate according to the expected faulty entities position in the ranking. Inside **[evaluator.py](evaluator.py)** there is more information and documentation.

Each scenario json file must contain the following attributes:

* **"good_logs_path"** : path of the good executions logs
* **"faulty_logs_path"** : path of the faulty executions logs
* **"good_logs_exchange"** : MQ exchange to send the good executions logs
* **"faulty_logs_exchange"** : MQ exchange to send the bad executions logs
* **"faulty_entities"** : List of faulty entities expected to be in the rankings. List of object with "name" and "parent", containing the name of the faulty entity and the name of its parent, respectively.

> ***TIP***: If you don't expect any method entities, only service, just place a random "name" and the service name in "parent". Then in the evaluator, in **evaluate_scenario()**, change the argument *parent_weight* in **calculate_ranking_accuracy()** to **1**.

The prerequisites are the same for the tool, since it is executed inside the evaluation.

However, depending on the logs specified in the paths, a different configuration might be necessary. Check the log processor [README](../microservices-log-processor/README.md) to understand how to do this.

To run the evaluator then simply execute: ```pipenv run python evaluator.py```
