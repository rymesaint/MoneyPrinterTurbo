import ast, json, unittest
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
WEBUI_I18N_DIR = ROOT_DIR / "webui" / "public" / "i18n"


def _load_translation(locale: str) -> dict:
    return json.loads((WEBUI_I18N_DIR / f"{locale}.json").read_text(encoding="utf-8")).get("Translation", {})


def _get_referenced_locales() -> list[str]:
    """Read locales listed in Nuxt config."""
    config_path = ROOT_DIR / "webui" / "nuxt.config.ts"
    text = config_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "locales:" in line and "[" in line:
            start = line.index("[")
            end = line.index("]", start) + 1
            return ast.literal_eval(line[start:end])
    return []


class TestWebuiI18n(unittest.TestCase):
    """Validate i18n JSON files against each other (all must match English keys)."""

    def test_all_locales_have_same_keys_as_english(self):
        en_keys = set(_load_translation("en"))
        for lang in sorted(WEBUI_I18N_DIR.glob("*.json")):
            loc = lang.stem
            if loc == "en":
                continue
            loc_keys = set(_load_translation(loc))
            missing = en_keys - loc_keys
            self.assertEqual(
                sorted(missing), [],
                f"{loc} missing keys from English: {sorted(missing)}",
            )
            extra = loc_keys - en_keys
            self.assertEqual(
                sorted(extra), [],
                f"{loc} has extra keys not in English: {sorted(extra)}",
            )

    def test_english_locale_has_keys(self):
        en = _load_translation("en")
        self.assertGreater(len(en), 100, "English locale has too few keys")
