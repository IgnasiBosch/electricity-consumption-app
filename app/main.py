"""
Electricity Consumption Web Application

"""

import asyncio
import json
import logging
import sys

import click

from app.infrastructure import http


@click.command()
@click.option(
    "-c",
    "--config",
    type=click.File("r"),
    default="./config.json",
    help="Configuration file",
)
def main(config):
    """entry point to run the application"""

    config = json.load(config)
    logging.basicConfig(
        stream=sys.stdout,
        level=config["logging_level"],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.log(logging.INFO, "Starting application")
    loop = asyncio.get_event_loop()
    http.run(loop, config)
