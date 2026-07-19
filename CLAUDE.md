# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado atual

Monorepo com dois deployables independentes na Cloudflare, hospedados no mesmo domínio (`/api/*` roteado para o backend):

- **`frontend/`** — Astro (output estático) + Tailwind v4 + MDX + sitemap. Deploy como Worker de assets estáticos (Workers Builds, git-connected).
- **`backend/`** — Worker Python nativo (Pyodide), estruturado em `src/lib/router.py` + `src/handlers/` + `src/services/`. Ainda sem lógica de LLM implementada (`chat.py`, `services/llm.py` e `services/logging.py` são stubs com TODO).

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

```
npm install                # instala o wrangler CLI local
npx wrangler dev            # roda o Worker Python localmente
npx wrangler deploy
```

- `wrangler.toml`: `compatibility_flags = ["python_workers"]`, `main = "src/entry.py"`.
- Segredos locais em `backend/.dev.vars` (não commitado — copie de `.dev.vars.example`); em produção via `npx wrangler secret put NOME`.
- D1 (`ai-logs`) e KV estão comentados no `wrangler.toml` como placeholder — ainda não provisionados (exige `wrangler login` numa conta Cloudflare real, depois `wrangler d1 create` / `wrangler kv namespace create` e colar os IDs).
- Chamadas a LLM devem usar `fetch` nativo do JS (módulo `js`), não os SDKs oficiais Python — eles costumam usar transporte síncrono, incompatível com o runtime assíncrono do Pyodide. Ver comentário em `src/services/llm.py`.
- Rota `/api/*` same-origem com o frontend está comentada no `wrangler.toml` (`routes`), à espera do domínio ser colocado na Cloudflare.

## Coisas ainda não resolvidas

- Domínio custom / zona na Cloudflare (necessário para a rota `/api/*` funcionar sem CORS).
- Provisionamento de D1 e KV do backend.
- Lógica real de chamada a LLM, streaming e log de prompts (`backend/src/handlers/chat.py`, `services/llm.py`, `services/logging.py`).
