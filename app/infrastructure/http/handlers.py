"""
Handlers of the endpoints, these are the dispatcher controllers of the requests

"""

import json
from dataclasses import asdict
from typing import Optional

import aiohttp_cors
from aiohttp import web

from app.infrastructure.data_source import DataSource
from app.infrastructure.http.constants import DATA_SOURCE_DEP, OPENAPI_DEP
from app.infrastructure.http.helpers import get_current_country_by_ip
from app.usecase.electricity_access import electricity_access
from app.usecase.energy_consumption import energy_consumption_per_capita


def setup_handlers(app: web.Application):
    """Register the endpoints"""
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*"
            )
        },
    )

    cors.add(app.router.add_get("/", main_handler))
    cors.add(app.router.add_get("/health", health_check_handler))
    cors.add(app.router.add_get("/v1/openapi", openapi_handler))
    cors.add(app.router.add_get("/v1/energy-consumption", energy_consumption_handler))
    cors.add(app.router.add_get("/v1/electricity-access", electricity_access_handler))
    cors.add(app.router.add_get("/v1/country/{country}", by_country_handler))


async def main_handler(request: web.Request):
    return web.json_response(
        [
            {
                route.method: route.resource.canonical
                if route.resource
                else str(route.resource)
            }
            for route in request.app.router.routes() if route.method in {"GET"}
        ]
    )


async def health_check_handler(_: web.Request):
    return web.json_response({"status": "OK"})


async def openapi_handler(request: web.Request):

    return web.Response(
        content_type="application/json",
        body=json.dumps(request.config_dict[OPENAPI_DEP]),
    )


async def energy_consumption_handler(request: web.Request) -> web.Response:
    data_source: DataSource = request.config_dict[DATA_SOURCE_DEP]
    current_country: Optional[str] = request.query.get(
        "country"
    ) or get_current_country_by_ip(request.remote)

    result = energy_consumption_per_capita(data_source, current_country, 10)

    return web.json_response(asdict(result))


async def electricity_access_handler(request: web.Request) -> web.Response:
    data_source: DataSource = request.config_dict[DATA_SOURCE_DEP]
    current_country: Optional[str] = request.query.get(
        "country"
    ) or get_current_country_by_ip(request.remote)

    top, bottom = electricity_access(data_source, current_country, 10)

    return web.json_response({"top": asdict(top), "bottom": asdict(bottom)})


async def by_country_handler(request: web.Request) -> web.Response:
    data_source: DataSource = request.config_dict[DATA_SOURCE_DEP]
    country = request.match_info.get("country")

    energy_consumption_result = data_source.energy_consumption_per_capita_by_country(
        country
    )
    electricity_access_result = data_source.electricity_ranking_by_country(country)

    return web.json_response(
        [asdict(energy_consumption_result), asdict(electricity_access_result)]
    )
