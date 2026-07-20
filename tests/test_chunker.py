import unittest

from qocha.chunker import CHUNK_MAX, CHUNK_TARGET, chunk_markdown, title_of


class TitleTests(unittest.TestCase):
    def test_h1_wins(self):
        self.assertEqual(title_of("a/b.md", "# The Title\nbody"),
                         "The Title")

    def test_frontmatter_title(self):
        text = "---\ntitle: 'From Frontmatter'\n---\nbody"
        self.assertEqual(title_of("a/b.md", text), "From Frontmatter")

    def test_stem_fallback(self):
        self.assertEqual(title_of("wiki/my-note.md", "just body"),
                         "my-note")


class ChunkTests(unittest.TestCase):
    def test_heading_paths(self):
        text = ("# T\nintro line " + "x" * CHUNK_TARGET +
                "\n## Alpha\nalpha body " + "y" * CHUNK_TARGET +
                "\n### Deep\ndeep body " + "z" * CHUNK_TARGET)
        chunks = chunk_markdown(text, "T")
        headings = [h for h, _ in chunks]
        self.assertIn("T", headings)
        self.assertIn("T > Alpha", headings)
        self.assertIn("T > Alpha > Deep", headings)

    def test_small_sections_merge(self):
        text = "# T\n## A\nshort a\n## B\nshort b\n## C\nshort c"
        chunks = chunk_markdown(text, "T")
        self.assertEqual(len(chunks), 1)
        # every constituent's text is still present in the merged chunk
        merged = chunks[0][1]
        for frag in ("short a", "short b", "short c"):
            self.assertIn(frag, merged)

    def test_oversized_sections_hard_split(self):
        text = "# T\n## Big\n" + "\n".join("line " + "w" * 80
                                           for _ in range(200))
        chunks = chunk_markdown(text, "T")
        self.assertGreater(len(chunks), 1)
        for _, chunk in chunks:
            self.assertLessEqual(len(chunk), CHUNK_MAX)

    def test_frontmatter_stripped(self):
        text = "---\ntags: [x]\n---\n# T\nreal body"
        chunks = chunk_markdown(text, "T")
        self.assertNotIn("tags:", chunks[0][1])
        self.assertIn("real body", chunks[0][1])


if __name__ == "__main__":
    unittest.main()
