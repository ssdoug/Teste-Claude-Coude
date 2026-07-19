from workers import Response


async def on_fetch(request):
    return Response.json({"message": "Hello from Python on Cloudflare Workers"})
