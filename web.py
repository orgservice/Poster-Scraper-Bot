import asyncio
from aiohttp import web, ClientSession, ClientTimeout

from config import Config

async def _start_web():
    r = web.RouteTableDef()

    @r.get("/", allow_head=True)
    async def _root(req):
        return web.json_response({"status": "running", "Creator": "@IMAXPRIME"})

    @r.get("/health", allow_head=True)
    async def _health(req):
        return web.json_response({"status": "healthy"})

    app = web.Application(client_max_size=30_000_000)
    app.add_routes(r)

    runner = web.AppRunner(app, access_log=None) 
    await runner.setup()

    port = Config.PORT
    await web.TCPSite(runner, "0.0.0.0", port).start()

async def _ping(url, interval):
    if not url:
        return

    await asyncio.sleep(60)

    while True:
        await asyncio.sleep(interval)
        try:
            async with ClientSession(
                timeout=ClientTimeout(total=10)
            ) as session:
                async with session.get(url) as resp:
                    print(f"Pinged: {resp.status}")
        except Exception:
            pass
