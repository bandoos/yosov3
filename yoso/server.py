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
import uvicorn
import yoso.utils as utils
from yoso.console import console
from yoso.config import ServerConfig
from yoso.core import config


class Server:

    def __init__(self, conf: ServerConfig):
        self.conf = conf
        self._setup()

    def _setup(self):
        """Run necessary pre-serve steps.
        1. ensure upload_dir exists
        """

        console.log("[green]Server setup[/]")
        utils.ensure_upload_dir(self.conf.upload_dir)
        console.log("Upload directory is: ", self.conf.upload_dir)
        # TODO:
        # - make sure models are loaded to avoid cold start requests
        # - setup logging/monitoring/audit tooling

    def _serve(self):
        "Dispatch the appropriate `uvicorn.run` call."

        uvicorn.run(
            self.conf.hanlder,
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
