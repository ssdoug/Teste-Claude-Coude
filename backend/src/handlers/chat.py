from workers import Response

# TODO: chamar o LLM via services.llm (fetch nativo, ver arquitetura §4.3/§4.4)
# e repassar a resposta em streaming (ReadableStream) sem bufferizar.


async def handle_chat(request, env, ctx):
    return Response.json({"error": "not implemented"}, status=501)
