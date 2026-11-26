"""Tests for the Gravion Bot web shell command catalog.

These tests exercise only the web layer (web/server.py). They do not import
or run the original bot code.
"""

import http.client
import json
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server  # noqa: E402


class CatalogTests(unittest.TestCase):
    def test_catalog_entries_are_unique_and_well_formed(self):
        names = [item["command"] for item in server.COMMANDS]
        self.assertEqual(len(names), len(set(names)))
        for item in server.COMMANDS:
            self.assertTrue(item["command"].startswith("/"))
            self.assertTrue(item["description"].strip())

    def test_every_catalog_command_has_a_reply(self):
        for item in server.COMMANDS:
            reply = server.built_in_reply(item["command"])
            self.assertIsNotNone(reply, item["command"])
            self.assertTrue(reply.strip(), item["command"])

    def test_help_lists_every_command(self):
        help_text = server.help_reply()
        for item in server.COMMANDS:
            self.assertIn(item["command"], help_text)

    def test_projects_reply_lists_flagships_with_links(self):
        reply = server.projects_reply()
        for name, _ in server.PROJECTS:
            self.assertIn(name, reply)
            self.assertIn(f"https://github.com/gravion-ux/{name}", reply)

    def test_links_reply_contains_profile_links(self):
        reply = server.links_reply()
        self.assertIn(server.GITHUB_URL, reply)
        self.assertIn(server.PORTFOLIO_URL, reply)
        self.assertIn(server.PETS_URL, reply)

    def test_unknown_command_falls_through(self):
        self.assertIsNone(server.built_in_reply("/not-a-command"))
        self.assertIsNone(server.built_in_reply("hello there"))


class RoutingTests(unittest.TestCase):
    def test_request_path_ignores_query_and_fragment(self):
        self.assertEqual(server.request_path("/api/health?source=test"), "/api/health")
        self.assertEqual(server.request_path("/styles.css?v=1#top"), "/styles.css")
        self.assertEqual(server.request_path(""), "/")

    def test_routes_accept_query_strings(self):
        httpd = server.create_server(port=0)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            port = httpd.server_address[1]
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            conn.request("GET", "/api/health?source=test")
            response = conn.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(response.status, 200)
            self.assertTrue(payload["ok"])

            conn.request(
                "POST",
                "/api/chat?source=test",
                body=json.dumps({"message": "/ping", "session_id": "test"}),
                headers={"Content-Type": "application/json"},
            )
            response = conn.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(response.status, 200)
            self.assertIn("pong", payload["reply"])
            conn.close()
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
