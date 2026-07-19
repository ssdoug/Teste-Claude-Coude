from urllib.parse import urlparse

from workers import Response

from handlers.health import handle_health
from handlers.chat import handle_chat

ROUTES = {
    ("GET", "/api/health"): handle_health,
    ("POST", "/api/chat"): handle_chat,
}


async def route(request, env, ctx):
    path = urlparse(str(request.url)).path
    handler = ROUTES.get((request.method, path))
    if handler is None:
        return Response("Not Found", status=404)
    return await handler(request, env, ctx)
