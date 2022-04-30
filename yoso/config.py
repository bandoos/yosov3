"""
Module defining configuration parameters for the application.

configuration can be overriden via env variables with the prefix `YOSO_`
followed by the name of the of the configuration parameter field


"""
from pydantic import BaseSettings


class ServerConfig(BaseSettings):
    # tcp/ip
    host: str = "0.0.0.0"
    port: int = 8000
    # application level
    dev_mode: bool = False
    upload_dir: str = "/tmp/yoso_image_upload"
    title: str = 'Deploying a ML Model with FastAPI'
    hanlder: str = "yoso.core:app"
    # OpenTelemetry
    otel_instrument: bool = False
    otel_instrument_exporter: str = "console"
    service_name: str = "yoso_prediction_server"
    # Prometheus
    prometheus_metrics: bool = True

    class Config:
        env_prefix = "YOSO_"


class ZipkinExporterConfig(BaseSettings):
    endpoint: str = "http://localhost:9411/api/v2/spans"

    class Config:
        env_prefix = "YOSO_ZIPKIN_"
