# Gravion Bot

![Gravion Bot](assets/banner.svg)

**Gravion Bot** by **Priyanshu Kumar Thakur** ([gravion-ux](https://github.com/gravion-ux)) — terminal-first bot with a modern web command deck.

- Portfolio: https://gravion-ux.github.io/portfolio/
- X: https://x.com/gravion_ux
- Gravion Pets: https://github.com/gravion-ux/gravion-pets


Gravion Bot is Priyanshu Kumar Thakur's terminal-first bot project with a separate web command deck. The original bot workflow remains in the existing workspace packages; the web shell in `web/` adds browser access without changing the original bot logic.

## Install

Prerequisites: Node.js 24 and pnpm (the repo enforces pnpm — npm/yarn installs are rejected), plus a PostgreSQL database for the API server.

```sh
git clone https://github.com/gravion-ux/gravion-bot.git
cd gravion-bot
pnpm install
```

Set the required environment variable before starting the API server:

```sh
export DATABASE_URL="postgres://user:password@localhost:5432/gravion_bot"
```

The web command deck needs no install — it runs on the Python 3 standard library only (see [Web interface](#web-interface)).

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Web interface

```sh
python3 web/server.py
```

Open `http://127.0.0.1:8765`.

Built-in web commands:

- `/help` — list available web commands.
- `/pets` — show Gravion Pets info and link.
- `/status` — show web shell and bot endpoint status.

Gravion Pets: https://github.com/gravion-ux/gravion-pets

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)
- Web shell: Python standard library HTTP server + static HTML/CSS/JS

## Where things live

- `artifacts/api-server/` — original API/bot server package
- `lib/` — shared workspace libraries
- `scripts/` — workspace scripts
- `web/` — separate browser shell, commands panel, and Gravion Pets section

## Credit

Priyanshu Kumar Thakur

## License

MIT — see [LICENSE](LICENSE).
