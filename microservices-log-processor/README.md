# Microservice Log Processor

This tool is built to receive logs (already parsed or not), parse the data required for debugging in a standard format, and publish it in an MQ in a RabbitMQ server, as to be later collected.

The prerequisites for this tool are to have Docker and Python (optional) installed. Docker is required to run the RabbitMQ server and the Logstash Pipeline.

The setup here detailed is meant for a local environment. Using it in a cloud/clustered environment should not affect the major parts, only the networking configuration.

## RabbitMQ Server

Run the RabbitMQ server using Docker.

```powershell
docker run --rm -dp 5672:5672 rabbitmq 
```

> --rm to remove the container when stopped, -d to run in detached mode, and -p to publish port 5672

Do not forget to start the server before using the tool. Note also that the default user ```guest:guest``` is used. Outside of local environments another user should be used ([source](https://www.rabbitmq.com/access-control.html#default-state)).

## Configuring Logstash

### Pipeline

Place any configuration for the logstash pipeline here, the input and output sources, as well as the filtering/formatting.

The files must follow the extension **\*.conf**. Follow [docs](https://www.elastic.co/guide/en/logstash/current/configuration-file-structure.html) for further info.

### Parsing logs

To parse the log into a structured and standardized format, inside the configuration file, leverage the ```filter``` section to build your *pattern*. In particular, [grok](https://www.elastic.co/guide/en/logstash/8.1/plugins-filters-grok.html) and [dissect](https://www.elastic.co/guide/en/logstash/8.1/plugins-filters-dissect.html).

Example log:

```verilog
2014-07-02 20:52:39 DEBUG className:200 - This is debug message
```

Filter section:

```less
filter {
  grok {
    match => {
      "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:logLevel}%{SPACE}%{JAVAFILE:className}:%{NUMBER:logLine:int} - %{GREEDYDATA:logMessage}"
    }
  }
}
```

Logstash output:

```json
{
  "@timestamp": "2022-03-08T16:28:35.026192Z",
  "@version": "1",
  "className": "className",
  "event": {
    "original": "2014-07-02 20:52:39 DEBUG className:200 - This is debug message\r"
  },
  "logLevel": "DEBUG",
  "logLine": 200,
  "logMessage": "This is debug message\r",
  "message": "2014-07-02 20:52:39 DEBUG className:200 - This is debug message\r",
  "timestamp": "2014-07-02 20:52:39"
}
```

By default, logstash produces this json when reading a log:

```json
{
  "@timestamp": "TIMESTAMP_WHEN_PROCESSED",
  "@version": "1",
  "event": {
    "original": "LOG_ENTRY"
  },
  "message": "LOG_ENTRY"
}
```

Other fields may appear according to the input plugin used, but those are common.

When matching a pattern in a log, it's possible to store a specific value inside the pattern. For example, the section ```%{LOGLEVEL:log_level}``` if it matches to a log level (info, warn, error,...) stores the value in **log_level**. This way you can extract any info present in the log and present it in any way you want.

If there are two input sources, with different logs, you can use multiple patterns in the grok matcher.

It's also possible to modify the fields already present, rename or remove them. Look into the [mutate](https://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html) filter for more details.

### *pipelines.yml*

It's possible to have multiple pipelines executing in logstash, see [here](https://www.elastic.co/guide/en/logstash/current/multiple-pipelines.html#multiple-pipeline-usage) for its usages.

Add new pipelines to logstash in ```logstash/config/pipelines.yml```.

Simple configuration is to add to the file:

```yaml
- pipeline.id: PIPELINE_ID_HERE
  path.config: "/usr/share/logstash/pipeline/PIPELINE_CONFIG_FILE"
```

For more pipeline configuration options, visit the [docs](https://www.elastic.co/guide/en/logstash/current/logstash-settings-file.html). (The syntax of each pipeline is the same as ```logstash.yml```)

### Docker image

To build the image (first run or if it is modified):

```powershell
docker build -t logstash .
```

To run the container, use the command:

```powershell
docker run --rm -it --network="host" --mount type=bind,source="$(pwd)"/data,target=/data logstash
```

## How to run

The steps to take sequently are:

1. Run the RabbitMQ server in the Docker image.
2. Run the Python script for the RabbitMQ messages receiver (```rabbit_mq_receive.py```)
3. Run the Logstash in Docker image
   1. The file will be read and first results can be seen
4. Run the Python script for the RabbitMQ messages sender (```rabbit_mq_send.py```)
   1. The logs will be parsed by Logstash and sent to the receiver
5. The Logstash instance will keep running, add more logs in ```log4jexamples.log``` or send logs to exchange ```logstash-input``` (follow the script above) in RabbitMQ, to keep processing logs
6. Stop the receiver program to write the contents in the json file (```logstash-rabbitmq.json```), the messages received meanwhile will be printed in the terminal

## Versions

* ELK: v8.0.1
* Logstash: OSS version, v8.0.1
* RabbitMQ: latest
