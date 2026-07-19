from workers import Response


async def handle_health(request, env, ctx):
    return Response.json({"status": "ok"})
