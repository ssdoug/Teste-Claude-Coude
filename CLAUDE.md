# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado atual

Monorepo com dois deployables independentes na Cloudflare, hospedados no mesmo domínio (`/api/*` roteado para o backend):

- **`frontend/`** — Astro (output estático) + Tailwind v4 + MDX + sitemap. Deploy como Worker de assets estáticos (Workers Builds, git-connected).
- **`backend/`** — Worker Python nativo (Pyodide), estruturado em `src/lib/router.py` + `src/handlers/` + `src/services/`. `/api/health` e `/api/chat` (Anthropic, sem streaming ainda) funcionando e deployados em `https://ai-backend.rom-doug10.workers.dev` (nome do Worker: `ai-backend`). `services/logging.py` ainda é stub (Fase 2 — D1/KV).

Cada pasta tem seu próprio `package.json`/lockfile (npm, sem workspaces — decisão explícita, não usar pnpm).

## Frontend (`frontend/`)

```
npm install
npm run dev      # astro dev
npm run build    # gera frontend/dist
npm run preview
```

- Content collections em `src/content.config.ts` (API nova do Astro 5+/7 — **não** criar `src/content/config.ts`, isso quebra o build com `LegacyContentConfigError`).
- `astro.config.mjs` tem `site: 'https://example.com'` como placeholder — trocar pelo domínio real antes do deploy final (o `@astrojs/sitemap` depende disso).
- Deploy via Cloudflare Workers Builds (dashboard, git-connected):
  - **Root directory do projeto no dashboard: `frontend`** (não `/`) — sem isso o build roda na raiz do repo, que não tem `package.json`, e falha.
  - Build command: `npm install && npm run build`
  - Deploy command: `npx wrangler deploy`
  - `frontend/wrangler.jsonc` define `assets.directory: "./dist"` e o `name` precisa bater com o nome do projeto já criado no dashboard da Cloudflare.

## Backend (`backend/`)

**⚠️ No Windows, o desenvolvimento do backend só funciona dentro do WSL.** O `entry.py` usa `from workers import WorkerEntrypoint` (SDK externo `workers-py`), que só é vendorizado no bundle via `pywrangler` (que usa `uv` por baixo). O `uv` nativo do Windows tem um bug ao consultar o interpretador Python-Pyodide (`ModuleNotFoundError: No module named 'python'`, reproduzível com `uv venv --python cpython-3.13.2-emscripten-wasm32-musl`) — sem WSL, nem `wrangler dev` puro funciona (dá `ModuleNotFoundError: No module named 'workers'`) nem `pywrangler`. Dentro do WSL (Ubuntu) funciona normalmente.

```bash
# Sempre dentro do WSL (wsl, depois cd /mnt/e/.../backend):
curl -LsSf https://astral.sh/uv/install.sh | sh   # uv (uma vez só)
# node via nvm (uma vez só) — precisa de Node no PATH pro pywrangler
npm install          # ⚠️ instala binários nativos (workerd/esbuild) — rode SEMPRE
                      # do mesmo SO que vai rodar depois (WSL aqui). Se rodar esse
                      # `npm install` no PowerShell do Windows depois, quebra os
                      # binários do lado WSL (e vice-versa) porque node_modules/
                      # é a mesma pasta física nos dois ambientes.
uv run pywrangler dev       # roda o Worker Python localmente
uv run pywrangler deploy
```

- `wrangler login` e `wrangler secret put` precisam ser rodados **de dentro do WSL** também (`node_modules/.bin/wrangler ...`) — a sessão de auth do Windows não é compartilhada com o WSL (configs em pastas separadas).
- `wrangler.toml`: `compatibility_flags = ["python_workers"]`, `main = "src/entry.py"`. `workers-py` está listado como dev dependency em `pyproject.toml` (`[dependency-groups] dev`), gerenciado pelo `uv` (não editar `uv.lock` na mão).
- Segredos locais em `backend/.dev.vars` (não commitado — copie de `.dev.vars.example`); em produção via `wrangler secret put NOME` (dentro do WSL).
- **Gotcha de interop**: `env.ALGUM_BINDING` lança `AttributeError` (não devolve `None`) quando o binding/secret não existe — usar `getattr(env, "NOME", None)`.
- D1 (`ai-logs`) e KV estão comentados no `wrangler.toml` como placeholder — ainda não provisionados.
- Chamadas a LLM usam `fetch` nativo do JS (módulo `js`), não os SDKs oficiais Python — eles costumam usar transporte síncrono, incompatível com o runtime assíncrono do Pyodide. Ver `src/services/llm.py` (headers como lista de pares `[[chave, valor], ...]`, não dict — evita o dict virar `Map` no JS, que `Headers`/`fetch` não aceitam).
- Rota `/api/*` same-origem com o frontend está comentada no `wrangler.toml` (`routes`), à espera do domínio ser colocado na Cloudflare. O frontend já está no ar em `toolboxai.com.br` (Worker `testeapisia`).

## Coisas ainda não resolvidas

- Domínio custom / zona na Cloudflare (necessário para a rota `/api/*` funcionar sem CORS) — ativar na Fase 2.
- Provisionamento de D1 e KV do backend.
- Streaming da resposta do Claude (hoje `handle_chat` bufferiza e devolve JSON de uma vez) e log de prompts (`services/logging.py` ainda é stub).
- `backend/node_modules` está instalado para Linux (WSL) no momento — rodar `npm install` de dentro do WSL sempre que precisar reinstalar.
