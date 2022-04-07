# Generator script

To generate dummy data use the generator at [json-generator](https://json-generator.com)

## Script

```json
[
  '{{repeat(5, 7)}}',
  {
    correlationID: '{{guid()}}',
    durationProcessing: '{{integer(10, 10000)}}',
    spanID: '{{guid()}}',
    endpoint: '/{{lorem(1, "words")}}',
    httpCode: '{{integer(400, 518)}}',
    instanceIP: '{{integer(0, 255)}}.{{integer(0, 255)}}.{{integer(0, 255)}}.{{integer(0, 255)}}',
    methodInvocation: {
      fileName: '{{lorem(1, "words")}}',
      line: '{{integer(1, 1000)}}',
      methodName: '{{lorem(1, "words")}}'
    },
    logLevel: '{{random("TRACE","INFO","DEBUG","WARN","ERROR","FATAL")}}',
    message: '{{lorem()}}',
    microserviceName: '{{lorem(1, "words")}}',
    parentSpanID: '{{guid()}}',
    timestamp: '{{date(new Date(2010,0,1), new Date(), "YYYY-MM-ddTHH:mm:ss Z")}}',
    user: '{{lorem(1, "words")}}'
  }
]
```
