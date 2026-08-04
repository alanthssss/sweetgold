import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class BilingualDocumentationTests(unittest.TestCase):
    def test_every_primary_markdown_document_has_a_chinese_peer(self):
        primary_documents = sorted(
            path
            for path in ROOT.rglob("*.md")
            if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
            and "node_modules" not in path.parts
            and not path.name.endswith(".zh-CN.md")
        )
        missing = [
            str(path.relative_to(ROOT))
            for path in primary_documents
            if not path.with_name(f"{path.stem}.zh-CN.md").is_file()
        ]
        self.assertEqual(missing, [])

    def test_document_pairs_link_to_each_other(self):
        failures = []
        for chinese in ROOT.rglob("*.zh-CN.md"):
            relative_parts = chinese.relative_to(ROOT).parts
            if any(part.startswith(".") for part in relative_parts) or "node_modules" in relative_parts:
                continue
            english = chinese.with_name(chinese.name.replace(".zh-CN.md", ".md"))
            if not english.is_file():
                failures.append(f"missing English peer for {chinese.relative_to(ROOT)}")
                continue
            english_text = english.read_text(encoding="utf-8")
            chinese_text = chinese.read_text(encoding="utf-8")
            if chinese.name not in english_text:
                failures.append(f"English link missing in {english.relative_to(ROOT)}")
            if english.name not in chinese_text:
                failures.append(f"English backlink missing in {chinese.relative_to(ROOT)}")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
