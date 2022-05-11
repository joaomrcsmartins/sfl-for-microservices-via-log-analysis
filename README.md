# thesis-meic-debugging-microservices-applications

Code repository that supports my Master Thesis. The goal is to develop a novel technique for debugging microservices by leveraging logging and tracing information and applying an SFL (spectrum-based fault localization) technique based on that information.

The project is two-fold (at the moment). First, there must be a way to parse log information and extract it in a programmable format. The project files dedicated to it are in [microservices-log-processor](https://github.com/joaomrcsmartins/thesis-meic-debugging-microservices-applications/tree/main/microservices-log-processor).

The second part dedicated to fault localization assumes the data is formatted correctly and ready for consumption. The project files dedicated to it are in [microservices-debugging-tool](https://github.com/joaomrcsmartins/thesis-meic-debugging-microservices-applications/tree/main/microservices-debugging-tool).

Each module has proper documentation and instructions on setting up and running.

## Demos

> TIP: you should read both modules docs before jumping to the demos to get a better idea how the tool works and its flow

Here are some demos to present the tool functioning and how to customize the tool the different scenarios.

### SFL Simple Demo Application

This demo is based on the SFL simple demo application, [Pet-A-Pet](https://github.com/joaomrcsmartins/sfl-simple-demo).

For the log processor, make sure the following pipeline is uncommented:

```yaml
- pipeline.id: logtstash-sfl-demo-petapet
  path.config: "/usr/share/logstash/pipeline/logstash-sfl-demo.conf"
```

You can set up the different parts (log processor, debugging tool, application) in any order. The only requirement is that the logs are only sent after all the components are running (i.e executing the *logs_sender.py* specified in the application's instructions).

After sending the logs when entities are first created the logs show it on the console (if the logger's logging levels are unchanged).
Once the log sender script has terminated and the debugging tool is no longer creating new entities, you can terminate the receival with CTRL+C.
The SFL debugging tool will process the entities and rank them, as explained in the tool's module.

### Instana's Robot Shop

This demo is based on [Instana's Robot Shop](https://github.com/instana/robot-shop) demo application.

There are some changes to the docker-compose file to help log shipping to the log processor. The changes are stored in [microservices-log-processor/data/robot-shop/](microservices-log-processor/data/robot-shop/). Just copy the contents to the files in the original repo.

It is also necessary to create docker network named **robot-shop-network**. See how to [here](https://docs.docker.com/engine/reference/commandline/network_create/).

For the log processor, make sure the following pipeline is uncommented:

```yaml
- pipeline.id: logstash-robot-shop
  path.config: "/usr/share/logstash/pipeline/logstash-robot-shop.conf"
```

To execute with the load generator in *docker-compose-load.yaml* you will need to run the tool twice, once with ERROR=0 (environment variable) and another with ERROR=1. Don't forget to change the output file in each run (Both are already present, just comment one and uncomment the other).

After you change the configuration of the log processor don't forget to (re)build the image:

```powershell
docker build -t log-processor .
```

And in this scenario, only, the command to execute the log processor will be:

```powershell
docker run --rm -it --network="robot-shop-network" --mount type=bind,source="$(pwd)"/data,target=/data log-processor
```

The processed logs will be in *microservices-log-processor/data/logs/*

To send the logs to the debugging tool you can create your own logstash configuration file, making sure each file of logs goes to the proper MQ channel, **logstash-output-good** or **logstash-output-bad**. Have the debugging tool running before sending the logs, naturally.

Or, to avoid the extra trouble, create a evaluation scenario inside **microservices-debugging-tool/test_scenarios/**. Then you just have to run the evaluator as specified in the [README](microservices-debugging-tool/README.md). A example for the robot shop is already available.
The log processor must have this pipeline active:

```yaml
- pipeline.id: logstash-robot-shop-evalutor
  path.config: "/usr/share/logstash/pipeline/logstash-robot-shop-eval.conf"
```
