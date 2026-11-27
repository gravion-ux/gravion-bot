import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import server


class ServerHelpersTest(unittest.TestCase):
    def test_clean_text_strips_nul_and_truncates(self):
        self.assertEqual(server.clean_text("a\x00b", 10), "ab")
        self.assertEqual(server.clean_text("abcdef", 3), "abc")
        self.assertEqual(server.clean_text(None, 3), "")

    def test_built_in_commands(self):
        self.assertIn("/help", server.built_in_reply("/help"))
        self.assertIsNone(server.built_in_reply("hello"))

    def test_configured_port_validation(self):
        old = os.environ.get("GRAVION_WEB_PORT")
        try:
            os.environ["GRAVION_WEB_PORT"] = "99999"
            with self.assertRaises(SystemExit):
                server._configured_port()
            os.environ["GRAVION_WEB_PORT"] = "8765"
            self.assertEqual(server._configured_port(), 8765)
        finally:
            if old is None:
                os.environ.pop("GRAVION_WEB_PORT", None)
            else:
                os.environ["GRAVION_WEB_PORT"] = old


if __name__ == "__main__":
    unittest.main()
