from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    ConsoleSpanExporter,
    BatchSpanProcessor,
)
from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter

from yoso.config import ZipkinExporterConfig


class BaseIntrumentationManager():

    def __init__(self, service_name):
        self.service_name = service_name
        self.tracer = trace.get_tracer(self.service_name)
        print("<---- tracer", self.tracer)
        self.provider = TracerProvider(
            resource=Resource.create({"service.name": self.service_name}))

    def configure(self):
        if not getattr(self, "processor"):
            raise Exception(
                "InstrumentationManager: processor was never registered")
        self.provider.add_span_processor(self.processor)

        trace.set_tracer_provider(self.provider)

    def get_provider(self):
        return self.provider


class ConsoleInstrumentationManager(BaseIntrumentationManager):

    def __init__(self, service_name):
        super().__init__(service_name)
        self.exporter = ConsoleSpanExporter()
        self.processor = SimpleSpanProcessor(self.exporter)
        self.configure()


class ZipkinInstrumentationManager(BaseIntrumentationManager):
    """
    docker run --rm -d -p 9411:9411 --name zipkin openzipkin/zipkin

    configured via yoso.config:ZipkinExporterConfig
    """

    # endpoint: str = "http://localhost:9411/api/v2/spans"

    def __init__(self, service_name):
        super().__init__(service_name)
        self.config = ZipkinExporterConfig()
        self.exporter = ZipkinExporter(endpoint=self.config.endpoint)
        self.processor = BatchSpanProcessor(self.exporter)
        self.configure()


options = {
    "console": ConsoleInstrumentationManager,
    "zipkin": ZipkinInstrumentationManager
}
