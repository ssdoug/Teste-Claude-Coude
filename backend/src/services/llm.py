import json

from js import fetch as js_fetch

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MODEL = "claude-sonnet-4-6"


async def call_anthropic(prompt: str, api_key: str) -> str:
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    })

    # Headers como lista de pares (não dict): o kwarg-bundling do Pyodide
    # converteria um dict Python em Map no JS, que o construtor de Headers/
    # fetch não aceita. Uma lista de [chave, valor] vira Array no JS, que é
    # o formato sequence<sequence> aceito.
    headers = [
        ["content-type", "application/json"],
        ["x-api-key", api_key],
        ["anthropic-version", ANTHROPIC_VERSION],
    ]

    response = await js_fetch(ANTHROPIC_URL, method="POST", headers=headers, body=payload)

    if not response.ok:
        error_text = await response.text()
        raise RuntimeError(f"Anthropic API error {response.status}: {error_text}")

    # .to_py() converte o JsProxy da resposta em dict/list nativos Python,
    # evitando depender de acesso por atributo/índice num proxy JS.
    data = (await response.json()).to_py()
    return data["content"][0]["text"]
