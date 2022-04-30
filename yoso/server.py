"""
Driver module for the server.

Wraps the setup and execution of the `yoso.core` module
into a `uvicorn` application.

The server is configured via pydantic BaseSettings derived class
which inferes default config override from ENV vars.

for development mode (i.e. with autoreload):
`export YOSO_dev_mode=TRUE` before running.


Invoking as main module will start server loop.

"""
import logging
import uvicorn
from importlib import import_module
# yoso imports
import yoso.utils as utils
from yoso.console import console
from yoso.config import ServerConfig
from yoso.core import config
# instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from yoso.tracer import ConsoleInstrumentationManager, ZipkinInstrumentationManager
import yoso.tracer as ytrace


class Server:
    instrument_exclude_urls = "metrics"

    def __init__(self, conf: ServerConfig):
        self.conf = conf
        self._setup()

    def _setup(self):
        """Run necessary pre-serve steps.
        1. ensure upload_dir exists
        2. resolve and setup monitoring instrumentation
        """

        console.log("[green]Server setup[/]")
        utils.ensure_upload_dir(self.conf.upload_dir)
        console.log("Upload directory is: ", self.conf.upload_dir)
        # setup logging/monitoring/audit tooling
        self.app = self._resolve_handler()
        # avoid logging metrics requests
        logging.getLogger("uvicorn.access").addFilter(
            utils.EndpointLogFilter(["/metrics"]))
        # TODO:
        # - make sure models are loaded to avoid cold start requests

    def _resolve_otel_manager(self):
        "Determine the instrumentation manager class to use"
        if self.conf.otel_instrument:
            choice = self.conf.otel_instrument_exporter
            cls = ytrace.options.get(choice)
            assert not (cls is None), f"Invalid exporter choice {choice}"
            return cls

    def _resolve_handler(self):
        """
        Workaround to allow open telemetry instrumentation
        Returns the specifier string if in dev mode or if instrumentation is off.
        Returns the instrumented FastAPI app if instrumentation is on.
        """
        if self.conf.dev_mode or (not self.conf.otel_instrument):
            console.log("[yellow]Open telemetry instrumentation is off![/]")
            # if dev mode or otel instrumentation turned off then
            # return handler as is
            return self.conf.hanlder
        else:
            console.log("[yellow]Open telemetry instrumentation is on![/]")
            # then we are in production mode and instrumentation is on
            (module_name, var_name) = self.conf.hanlder.split(":")
            assert not (module_name is None), "invalid handler specifier"
            assert not (var_name is None), "invalid handler specifier"
            mod = import_module(module_name)
            handler = getattr(mod, var_name)

            instrumentation_manager_cls = self._resolve_otel_manager()
            self.instrumentation_manager = instrumentation_manager_cls(
                self.conf.service_name)

            FastAPIInstrumentor.instrument_app(
                handler,
                tracer_provider=self.instrumentation_manager.get_provider(),
                excluded_urls=self.instrument_exclude_urls)
            return handler

    def _serve(self):
        "Dispatch the appropriate `uvicorn.run` call."

        uvicorn.run(
            self.app,
            host=self.conf.host,
            port=self.conf.port,
            reload=self.conf.dev_mode,
        )

    def __call__(self):
        "Print info and run server loop"

        host = self.conf.host
        port = self.conf.port

        if self.conf.dev_mode:
            console.log("[green]dev mode is: ON[/]")

        console.log(f"[yellow]=> [link={host}:{port}]{host}:{port}[/link][/]")

        self._serve()


if __name__ == "__main__":
    server: Server = Server(config)
    server()
