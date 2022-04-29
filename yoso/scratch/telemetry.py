from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    ConsoleSpanExporter,
    BatchSpanProcessor,
)
from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter
import time

service_name = "scratch_demo"
# 0 build provider
provider = TracerProvider()
# 1 build exporter
exporter = ZipkinExporter(endpoint="http://localhost:9411/api/v2/spans")
# 2 build processor from exporter
processor = BatchSpanProcessor(exporter)
# 3 Add processor to provider
provider.add_span_processor(processor)
# 4 set tracer provider
trace.set_tracer_provider(provider)
# 5 obtain tracer
tracer = trace.get_tracer(service_name)

with tracer.start_as_current_span("foo"):
    time.sleep(0.5)
    with tracer.start_as_current_span("bar"):
        time.sleep(0.5)
        with tracer.start_as_current_span("baz"):
            print("Hello OpenTelemetry!")
