#!/usr/bin/env python3
"""Standalone web shell for Gravion Bot.

This server does not import or modify the original bot code. It serves a
browser interface and forwards chat messages only when a separate bot endpoint
or one-shot command is configured by the operator.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
MAX_MESSAGE_CHARS = 4000
MAX_REPLY_CHARS = 12000
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}

PETS_URL = "https://github.com/gravion-ux/gravion-pets"

COMMANDS = [
    {"command": "/help", "description": "Show available web commands."},
    {"command": "/pets", "description": "Show Gravion Pets info and link."},
    {"command": "/status", "description": "Show web shell and bot endpoint status."},
]


def help_reply() -> str:
    lines = ["Gravion Bot commands:"]
    for item in COMMANDS:
        lines.append(f"{item['command']} — {item['description']}")
    lines.append("Send any other message to chat with the configured bot endpoint.")
    return "\n".join(lines)


def pets_reply() -> str:
    return (
        "Gravion Pets is Priyanshu Kumar Thakur's virtual pet project with collectible pets, "
        f"progression, and web play. Open it here: {PETS_URL}"
    )


def status_reply() -> str:
    state = "configured" if bot_configured() else "not configured yet"
    return f"Gravion Bot web shell is online. Bot endpoint: {state}. Built-in commands: /help, /pets, /status."


def built_in_reply(message: str) -> str | None:
    command = message.strip().split()[0].lower() if message.strip() else ""
    if command == "/help":
        return help_reply()
    if command == "/pets":
        return pets_reply()
    if command == "/status":
        return status_reply()
    return None


def clean_text(value: object, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    text = value.replace("\x00", "").strip()
    return text[:limit]


def bot_configured() -> bool:
    return bool(os.environ.get("GRAVION_BOT_API_URL") or os.environ.get("GRAVION_BOT_COMMAND"))


def forward_to_api(message: str, session_id: str) -> str:
    url = os.environ.get("GRAVION_BOT_API_URL", "").strip()
    payload = json.dumps({"message": message, "session_id": session_id}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read(65536).decode("utf-8", errors="replace")
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return clean_text(body, MAX_REPLY_CHARS)
    if isinstance(data, dict):
        for key in ("reply", "message", "text", "output"):
            reply = clean_text(data.get(key), MAX_REPLY_CHARS)
            if reply:
                return reply
    return clean_text(body, MAX_REPLY_CHARS)


def run_one_shot_command(message: str) -> str:
    command = os.environ.get("GRAVION_BOT_COMMAND", "").strip()
    args = shlex.split(command)
    if not args:
        raise ValueError("empty command")
    completed = subprocess.run(
        args,
        input=message,
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("bot command failed")
    return clean_text(completed.stdout, MAX_REPLY_CHARS)


def get_reply(message: str, session_id: str) -> str:
    if os.environ.get("GRAVION_BOT_API_URL"):
        return forward_to_api(message, session_id)
    if os.environ.get("GRAVION_BOT_COMMAND"):
        return run_one_shot_command(message)
    raise RuntimeError("not configured")


class GravionWebHandler(BaseHTTPRequestHandler):
    server_version = "GravionBotWeb/1.0"

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
        if self.path == "/api/health":
            self.send_json(200, {"ok": True, "bot_configured": bot_configured(), "commands": COMMANDS, "pets_url": PETS_URL})
            return
        if self.path == "/api/commands":
            self.send_json(200, {"ok": True, "commands": COMMANDS, "pets_url": PETS_URL})
            return
        static = STATIC_FILES.get(self.path)
        if not static:
            self.send_json(404, {"ok": False, "error": "Not found"})
            return
        filename, content_type = static
        path = WEB_DIR / filename
        if not path.is_file():
            self.send_json(404, {"ok": False, "error": "Not found"})
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler name
        if self.path != "/api/chat":
            self.send_json(404, {"ok": False, "error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > 32768:
            self.send_json(400, {"ok": False, "error": "Invalid request body"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"ok": False, "error": "Invalid JSON"})
            return
        message = clean_text(payload.get("message") if isinstance(payload, dict) else "", MAX_MESSAGE_CHARS)
        session_id = clean_text(payload.get("session_id") if isinstance(payload, dict) else "web", 80) or "web"
        if not message:
            self.send_json(400, {"ok": False, "error": "Message is required"})
            return
        built_in = built_in_reply(message)
        if built_in is not None:
            self.send_json(200, {"ok": True, "reply": built_in, "command": message.strip().split()[0].lower()})
            return
        if not bot_configured():
            self.send_json(
                503,
                {
                    "ok": False,
                    "error": "Bot endpoint is not configured yet. Set GRAVION_BOT_API_URL or GRAVION_BOT_COMMAND, then restart the web shell.",
                },
            )
            return
        try:
            reply = get_reply(message, session_id)
        except (RuntimeError, ValueError, subprocess.TimeoutExpired, urllib.error.URLError, OSError):
            self.send_json(502, {"ok": False, "error": "Bot endpoint did not return a reply"})
            return
        if not reply:
            self.send_json(502, {"ok": False, "error": "Bot endpoint returned an empty reply"})
            return
        self.send_json(200, {"ok": True, "reply": reply})


def create_server(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), GravionWebHandler)


def main() -> None:
    port = int(os.environ.get("GRAVION_WEB_PORT", "8765"))
    server = create_server(port=port)
    print(f"Gravion Bot web shell listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
