"""Heading-path chunking for markdown notes.

Split on ##/### headings, carry a "heading path" breadcrumb
(note > section > subsection) so citations stay human-legible, greedily
merge small adjacent sections toward a target size, hard-split oversized
ones. Extracted unchanged from a production vault index.
"""
import re
from pathlib import Path

CHUNK_TARGET = 1800          # chars (~450 tokens) to merge small sections to
CHUNK_MAX = 4000             # hard split ceiling


def title_of(path, text):
    """A note's display title: first H1, else frontmatter title, else stem."""
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        return m.group(1).strip()[:200]
    m = re.search(r"^---\n.*?^title:\s*(.+?)\s*$.*?^---", text, re.M | re.S)
    if m:
        return m.group(1).strip().strip("\"'")[:200]
    return Path(path).stem


def chunk_markdown(text, title):
    """[(heading_path, chunk_text)] — split on ##/### headings, merge small
    adjacent sections toward CHUNK_TARGET, hard-split past CHUNK_MAX."""
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    sections = []          # (heading_path, text)
    h2 = h3 = None
    buf = []

    def flush():
        chunk = "\n".join(buf).strip()
        if chunk:
            crumbs = [c for c in (title, h2, h3) if c]
            sections.append((" > ".join(crumbs), chunk))
        buf.clear()

    for line in body.splitlines():
        m2 = re.match(r"^##\s+(.+)$", line)
        m3 = re.match(r"^###\s+(.+)$", line)
        if m2:
            flush()
            h2, h3 = m2.group(1).strip()[:120], None
        elif m3:
            flush()
            h3 = m3.group(1).strip()[:120]
        else:
            buf.append(line)
    flush()

    merged = []
    for heading, chunk in sections:
        if merged and len(merged[-1][1]) + len(chunk) < CHUNK_TARGET:
            ph, pt = merged[-1]
            # keep the most specific heading path for the merged chunk and
            # leave the other constituent's heading visible in the text
            # (FTS still finds it; citations stay precise)
            if heading.count(" > ") >= ph.count(" > "):
                merged[-1] = (heading, f"[{ph}]\n{pt}\n\n{chunk}")
            else:
                merged[-1] = (ph, f"{pt}\n\n[{heading}]\n{chunk}")
        else:
            merged.append((heading, chunk))

    out = []
    for heading, chunk in merged:
        while len(chunk) > CHUNK_MAX:
            cut = chunk.rfind("\n", CHUNK_TARGET, CHUNK_MAX)
            cut = cut if cut > 0 else CHUNK_MAX
            out.append((heading, chunk[:cut].strip()))
            chunk = chunk[cut:].strip()
        if chunk:
            out.append((heading, chunk))
    return out
