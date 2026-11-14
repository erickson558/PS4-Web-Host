from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DashboardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = {}
        self.handlers = []

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if "id" in attributes:
            self.ids[attributes["id"]] = tag
        self.handlers.extend(
            (name, value)
            for name, value in attributes.items()
            if name in ("onclick", "onchange")
        )


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = DashboardParser()
        cls.page.feed((ROOT / "index.html").read_text(encoding="utf-8"))

    def test_existing_controls_remain_available(self):
        expected = {
            "pslogo": "button",
            "ps-logo-container": "div",
            "exploitRun": "button",
            "settings-popup-overlay": "div",
            "payloadsSection": "div",
            "PS4FW": "p",
        }
        for element_id, tag in expected.items():
            with self.subTest(element_id=element_id):
                self.assertEqual(self.page.ids.get(element_id), tag)
        self.assertIn(("onclick", "settingsPopup()"), self.page.handlers)
        self.assertIn(("onchange", "setLayout(this.value);"), self.page.handlers)
        self.assertIn(("onchange", "setTheme(this.value);"), self.page.handlers)

    def test_each_offline_manifest_lists_dashboard_styles(self):
        manifests = list((ROOT / "includes" / "caches" / "manifest").glob("*.manifest"))
        self.assertTrue(manifests)
        for manifest in manifests:
            with self.subTest(manifest=manifest.name):
                content = manifest.read_text(encoding="utf-8")
                self.assertIn("../../../includes/css/colors/default.css", content)
                self.assertIn("../../../includes/css/layouts/index.css", content)
                self.assertIn("../../../includes/css/layouts/compact.css", content)
                self.assertIn("../../../includes/assets/icons/ps4-web-host.svg", content)

    def test_primary_branding_uses_personal_host_name(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        cache = (ROOT / "cache.html").read_text(encoding="utf-8")
        exploit = (ROOT / "exploit.html").read_text(encoding="utf-8")
        self.assertIn("<title>PS4 Web Host</title>", index)
        self.assertIn("includes/assets/icons/ps4-web-host.svg", index)
        self.assertNotIn("Powered by WebKitty", index)
        self.assertIn("<title>PS4 Web Host - Caching</title>", cache)
        self.assertIn("<h4>PS4 Web Host</h4>", exploit)


if __name__ == "__main__":
    unittest.main()
