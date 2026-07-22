from workers import Response

from services.llm import call_anthropic


async def handle_chat(request, env, ctx):
    try:
        data = await request.json()
    except Exception:
        return Response.json({"error": "invalid json body"}, status=400)

    # request.json() no Python Workers pode devolver dict nativo ou proxy JS
    # dependendo da versão do runtime; cobre os dois formatos.
    if hasattr(data, "to_py"):
        data = data.to_py()
    prompt = data.get("prompt") if isinstance(data, dict) else None

    if not prompt:
        return Response.json({"error": "missing 'prompt' field"}, status=400)

    # env.ANTHROPIC_API_KEY lança AttributeError (em vez de devolver None) quando
    # o secret não está configurado — daí o getattr com default.
    api_key = getattr(env, "ANTHROPIC_API_KEY", None)
    if not api_key:
        return Response.json({"error": "ANTHROPIC_API_KEY not configured"}, status=500)

    try:
        text = await call_anthropic(prompt, api_key)
    except Exception as e:
        return Response.json({"error": str(e)}, status=502)

    return Response.json({"text": text})
