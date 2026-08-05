import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class BilingualDocumentationTests(unittest.TestCase):
    STRUCTURAL_PARITY_DOCUMENTS = (
        "README.md",
        "HANDOFF.md",
        "CHANGELOG.md",
        "docs/product-design.md",
        "docs/getting-started.md",
        "docs/impact-and-roadmap.md",
        "docs/release-checklist.md",
        "docs/releases/models-v1.md",
        "docs/releases/models-v2.md",
        "docs/releases/v1.0.0.md",
        "docs/releases/v1.0.1.md",
        "docs/releases/v1.1.0.md",
        "docs/releases/v1.2.0.md",
    )

    def test_readmes_have_the_same_section_structure(self):
        marker_pattern = re.compile(r"<!-- section:([a-z0-9-]+) -->")
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        english_sections = marker_pattern.findall(english)
        chinese_sections = marker_pattern.findall(chinese)

        self.assertGreater(len(english_sections), 0)
        self.assertEqual(english_sections, chinese_sections)
        self.assertEqual(english.count("```"), chinese.count("```"))

    def test_key_document_pairs_have_matching_structure(self):
        heading_pattern = re.compile(r"^(#{1,6}) ", re.MULTILINE)
        failures = []

        for relative_path in self.STRUCTURAL_PARITY_DOCUMENTS:
            english_path = ROOT / relative_path
            chinese_path = english_path.with_name(
                f"{english_path.stem}.zh-CN{english_path.suffix}"
            )
            english = english_path.read_text(encoding="utf-8")
            chinese = chinese_path.read_text(encoding="utf-8")
            english_headings = [len(marker) for marker in heading_pattern.findall(english)]
            chinese_headings = [len(marker) for marker in heading_pattern.findall(chinese)]

            if english_headings != chinese_headings:
                failures.append(
                    f"heading levels differ for {relative_path}: "
                    f"{english_headings} != {chinese_headings}"
                )
            if english.count("```") != chinese.count("```"):
                failures.append(f"code block counts differ for {relative_path}")

        self.assertEqual(failures, [])

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
