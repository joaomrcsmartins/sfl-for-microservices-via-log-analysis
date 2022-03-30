# thesis-meic-debugging-microservices-applications

Code repository that supports my Master Thesis. The goal is to develop a novel technique for debugging microservices by leveraging logging and tracing information and applying an SFL (spectrum-base fault localization) technique based on that information.

The project is two-fold (at the moment). First, there must be a way to parse log information and extract it in a programmable format. The project files dedicated to it are in [microservices-log-processor](https://github.com/joaomrcsmartins/thesis-meic-debugging-microservices-applications/tree/main/microservices-log-processor).

The second part dedicated to fault localization assumes the data is formatted correctly and ready for consumption. The project files dedicated to it are in [microservices-debugging-tool](https://github.com/joaomrcsmartins/thesis-meic-debugging-microservices-applications/tree/main/microservices-debugging-tool).

Each module has proper documentation and instructions on setting up and running.
