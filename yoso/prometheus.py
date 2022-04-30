from starlette_prometheus import metrics, PrometheusMiddleware
from fastapi import FastAPI


def add_metrics(app: FastAPI) -> FastAPI:
    """
    Add prometheus middleware and /metrics route to given app.
    """
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics)
