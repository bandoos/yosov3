"""
Entry point cli module to showcase how to build a CLI app
out of the prediction service os the yoso module
"""
import os
import click
from yosoclient.config import ClientConfig
from yosoclient.core import Client
from yosoclient.console import console
from rich.pretty import pprint

#
#

config = ClientConfig()
client = Client(config)


def check_extension(x):
    name, ext = os.path.splitext(x)
    return ext in config.accepted_formats


@click.group(help="Command line client for YOSO prediction service")
@click.option("--confidence", default=0.5, type=click.FLOAT)
@click.pass_context
def cli(ctx: click.Context, confidence):
    ctx.ensure_object(dict)
    ctx.obj["confidence"] = confidence
    pass


@cli.command(help="Predict bounding boxes and labels for a single image")
@click.pass_context
@click.option("--file", type=click.Path(exists=True), required=True)
@click.option("--dest-dir", type=click.Path(exists=True))
def predict_one(ctx, file, dest_dir):
    client.predict_request(file,
                           dest_dir=dest_dir,
                           confidence=ctx.obj["confidence"])


@cli.command(help="Predict bounding boxes and lables for a directory of images"
             )
@click.pass_context
@click.option("--source-dir", type=click.Path(exists=True), required=True)
@click.option("--dest-dir", type=click.Path(exists=True), required=True)
def predict_all(ctx, source_dir, dest_dir):
    assert os.path.isdir(source_dir), "--source-dir must be a directory"
    assert os.path.isdir(dest_dir), "--dest-dir must be a directory"

    paths = [
        os.path.join(source_dir, x) for x in os.listdir(source_dir)
        if check_extension(x)
    ]

    assert len(paths) > 0, "--source-dir must contain at least one image file"

    for path in paths:
        console.log(f"[green]Predict request for {path}[/]")
        client.predict_request(path,
                               dest_dir=dest_dir,
                               confidence=ctx.obj["confidence"])


@cli.command(help="Count objects present in a single image")
@click.pass_context
@click.option("--file", type=click.Path(exists=True), required=True)
def count_objects(ctx, file):
    data = client.count_objects_request(file, confidence=ctx.obj["confidence"])
    pprint(data)


if __name__ == "__main__":
    cli(obj={})
