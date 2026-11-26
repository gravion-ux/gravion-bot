"""Tests for the Gravion Bot web shell command catalog.

These tests exercise only the web layer (web/server.py). They do not import
or run the original bot code.
"""

import sys
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


if __name__ == "__main__":
    unittest.main()
