# Deploying a ML Model as prediction server using fastapi

Expose the basic pretrained yolo models from `cvlib`
via `cvlib.detect_common_objects` as a fastapi server.
This showcases a basic prediction server setup.

A request on the `/predict` endpoint passing the dired model name,
an optional confidence level, and an image file to process, will
produce a response being the image with delimiting boxes drawn,
and label indication (with confidence level annotation).

A request on the `/count_objects` endpoint will return a {items: Dict [str,int]}
structure with the counts of objects per label. The same inputs as `/predict` are required.

The server is configured via pydantic BaseSettings derived class
which inferes default config override from ENV vars.

for development mode (i.e. with autoreload):
`export YOSO_dev_mode=TRUE` before running.

This software is adapted from coursera `introduction-to-machine-learning-in-production`
ungraded lab week 1.


## Server configuration

The can be configured via ENV vars prefixed with `YOSO`
see the *yoso.config* module.

The default configuration values serves on port 8000 from all interfaces.
To run in development mode make sure to `$ source dev_env_vars` before running the server.
dev mode will turn on hot reload.

### Monitoring instrumentation
The prediction server can optionally be monitored via OpenTelemetry
instrumentation.  Instrumentation is available outside of dev_mode,
and is turned on by setting `YOSO_otel_instrument=TRUE`.

By default monitoring exports spans to the console. This is useful to
check everything is working but is undesirable in general. A more
useful setup is using a span collector like `zipkin`.

To enable zipkin monitoring set `YOSO_otel_instrument_exporter=zipkin`
and `YOSO_ZIPKIN_endpoint=http://<zipkin-host>:<zipkin-port>/api/v2/spans`.

A plug and play zipkin instance can be run via docker with:
`$ docker run --rm -d -p 9411:9411 --name zipkin openzipkin/zipkin`








## Installation

1. create and activate a virtual env for the project
   tested with python 3.8
2. `$ pip install -r requirements.txt`

## Run

Make sure the virtual env is activated.

`python -m yoso.server`


# Why yoso?
it's a pun on the YOLO model (you only look once), for "you only serve once"


# Client

The yosoclient also shows a simple approach to consume the API from python.
A simple CLI application using `click` shows how the client wrapper can be used.

see help via `$ python -m yosoclient.cli --help`.
