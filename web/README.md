# Gravion Bot Web Shell

This folder adds a separate browser interface beside the original bot workflow. The original bot files and workflow are unchanged.

## Run the web shell

```sh
python3 web/server.py
```

Open `http://127.0.0.1:8765`.

## Built-in web commands

- `/help` — list available web commands.
- `/pets` — show Gravion Pets info and link: https://github.com/gravion-ux/gravion-pets
- `/status` — show web shell and bot endpoint status.

These commands are handled by the web shell and do not modify the original bot code.

## Connect replies

Set one of these environment variables before starting the web shell:

- `GRAVION_BOT_API_URL` — an HTTP endpoint that accepts JSON with `message` and `session_id`, and returns JSON with `reply`.
- `GRAVION_BOT_COMMAND` — a one-shot terminal command that reads one message from standard input and writes one reply to standard output.

The original entrypoint remains in `artifacts/api-server/src/index.ts`. It is a long-running bot/server entrypoint, so the web shell does not import it or change its workflow.

Credit: Priyanshu Kumar Thakur
