import asyncio
import signal

from aiohttp import web

HEALTH = "/health"


async def health_check(_: web.Request):
    return web.json_response({"status": "OK"})


def run(host, port):
    # Initialize the HTTP server.
    app = web.Application()
    app.router.add_get(HEALTH, health_check)

    # Start the HTTP server.
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, loop.stop)
    web.run_app(app, host=host, port=port)
