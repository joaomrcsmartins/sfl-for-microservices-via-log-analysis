# Microservice Log Processor

This tool is built to receive logs (already parsed or not), parse the data required for debugging in a standard format, and publish it in an MQ in a RabbitMQ server, as to be later collected.

The prerequisites for this tool are to have Docker and Python (optional) installed. Docker is required to run the RabbitMQ server and the Logstash Pipeline.

The setup here detailed is meant for a local environment. Using it in a cloud/clustered environment should not affect the major parts, only the networking configuration.
## RabbitMQ Server

Run the RabbitMQ server using Docker.

```
docker run --rm -dp 5672:5672 rabbitmq (--rm to remove the container when stopped, -d to run in detached mode, and -p to publish port 5672)
```

Do not forget to start the server before using the tool.

## Configuring Logstash

### Pipeline

Place any configuration for the logstash pipeline here, the input and output sources, as well as the filtering/formatting.

The files must follow the extension **\*.conf**. Follow [docs](https://www.elastic.co/guide/en/logstash/current/configuration-file-structure.html) for further info.

#### Parsing logs

To parse the log into a structured and standardized format, inside the configuration file, leverage the ```filter``` section to build your *pattern*. In particular, [grok](https://www.elastic.co/guide/en/logstash/8.1/plugins-filters-grok.html) and [dissect](https://www.elastic.co/guide/en/logstash/8.1/plugins-filters-dissect.html).

Example log:
```verilog
2014-07-02 20:52:39 DEBUG className:200 - This is debug message
```
Filter section:
```wget co
filter {
  grok {
    match => {"message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:logLevel}%{SPACE}%{JAVAFILE:className}:%{NUMBER:logLine} - %{GREEDYDATA:logMessage}"}
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
  "host": {
    "name": "docker-desktop"
  },
  "log": {
    "file": {
      "path": "/data/log4jexamples.log"
    }
  },
  "logLevel": "DEBUG",
  "logLine": "200",
  "logMessage": "This is debug message\r",
  "message": "2014-07-02 20:52:39 DEBUG className:200 - This is debug message\r",
  "timestamp": "2014-07-02 20:52:39"
}
```
### *pipelines.yml*

To have multiple sources of logs collected by logstash, create a new pipeline specifying the proper configuration.

Add new pipelines to logstash in ```logstash/config/pipelines.yml```. 

Simple configuration is to add to the file:
```yaml
- pipeline.id: PIPELINE_ID_HERE
  path.config: "/usr/share/logstash/pipeline/PIPELINE_CONFIG_FILE"
```

For more pipeline configuration options, visit the [docs](https://www.elastic.co/guide/en/logstash/current/logstash-settings-file.html). (The syntax of each pipeline is the same as ```logstash.yml```)

### Docker image

To build the image (first run or if it is modified):
```
docker build -t logstash .
```

To run the container:
```
docker run --rm -it --network="host" logstash
```