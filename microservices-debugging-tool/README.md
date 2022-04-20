# Microservices Debugging Tool

The microservices debugging tool works by applying the known SFL technique on the information extraction from logs produced by microservices.

Once the logs have been processed by the log processor tool, they are sent to be collected.
This tool sets up communication to start receiving them with message queues.
They required to be separated into two different sets of logs, one belonging to correct executions of the microservices and the other belonging to faulty executions of the microservices.

By each log received, the log data is parsed into a entity object, which is the fundamental element of SFL.
In this approach, two types of entities are currently created, with different granularity. One is the Service Entity, which represents the (micro)service.
The represents the Method Entity, created when the log contains relevant data about the invoked method. Since log uniformity is not assumed or always feasible,
the tool accepts the two levels of granularity and ranks the two types together.

After receiving all the data, the communication is shutdown (currently manually) and collected entities are merged into unique entities with their references.

The analysis is the first part of the SFL techniques, which tracks the *hit spectra*, i.e., when an entity is executed or not in each unique request (execution).

Once that is complete, the ranking of the entities takes place, by applying one or more metrics currently available, and merging them using a common operator (mean or median at this moment).
Finally the ranked entities are sorted and the final result saved into a JSON file to be analyzed by the developer.

The tool also provides logging of the execution so that in each run the user can look into the steps of the tool and each component is properly documented.

## Prerequisites

* Python 3.X
* Pip

## Installation and setup

1. Install Pipenv: ```pip install --user pipenv```
2. Install dependencies: ```pipenv install```

## Running the application

1. You can activate the virtual environment with pipenv: ```pipenv shell```
   1. And inside start the application: ```python main.py```

2. Or instead, simply execute: ```pipenv run python main.py```
