import asyncio
import json
import signal
from typing import Mapping

import aiohttp
from aiohttp import web

from app.infrastructure.data_source import DataSource
from app.infrastructure.http.clients import HTTPClient, WorldBankV2Client
from app.infrastructure.http.constants import DATA_SOURCE_DEP, OPENAPI_DEP, TASKS_DEP
from app.infrastructure.http.handlers import setup_handlers


def on_startup(config: Mapping):
    async def startup_handler(app: web.Application):
        """Bootstrapping the server. Instantiates all needed objects and store them
        into the app as a DIC (Dependency injection container)"""

        client_session = aiohttp.ClientSession()
        http_client = HTTPClient(client_session)

        source = WorldBankV2Client(http_client, config["source_url"])
        energy_consumption = DataSource(source)
        await energy_consumption.update_values()
        app[DATA_SOURCE_DEP] = energy_consumption

        loop = asyncio.get_running_loop()
        task = loop.create_task(
            energy_consumption.update_task(
                interval_in_days=config["data_refresh_interval_in_days"]
            )
        )

        with open(config["openapi_filepath"]) as openapi_file:
            app[OPENAPI_DEP] = json.loads(openapi_file.read())

        app[TASKS_DEP] = []
        app[TASKS_DEP].append(task)

        async def cleanup(_: web.Application):
            """Perform required cleanup on shutdown"""
            await client_session.close()
            for _task in app[TASKS_DEP]:
                _task.cancel()
            await asyncio.wait(app[TASKS_DEP])

        app.on_shutdown.append(cleanup)

    return startup_handler


def run(loop, config: Mapping):
    """Run the server"""
    app = web.Application()
    app.on_startup.append(on_startup(config))
    setup_handlers(app)

    loop.add_signal_handler(signal.SIGTERM, loop.stop)
    web.run_app(app, host=config["host"], port=config["port"])
