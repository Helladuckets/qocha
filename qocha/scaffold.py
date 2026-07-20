"""`qocha init` — seed a three-layer vault.

Creates the missing layers and starter files for the pattern described
in conventions/the-pattern.md. Strictly additive: an existing file or
directory is never touched, so running it on a live vault only fills
gaps. Returns the list of vault-relative paths it created.
"""
import json
from datetime import date
from pathlib import Path

SCHEMA_STARTER = """# {name} — Schema

> **See also:** the qocha wiki spec (conventions/wiki-spec.md in the
> qocha repo) — this vault extends that foundation (three-layer
> pattern, ingest/query/lint/clean operations, density ladder,
> frontmatter shape). Everything below adds {name}-specific rules.
> Fill the {{{{params}}}} using conventions/adaptation-checklist.md.

## Purpose

{{{{CORPUS_DESCRIPTION — what this vault is, whose knowledge it holds,
whether sources are a live intake stream or a fixed archive.}}}}

## Directory layout

```
{name}/
├── CLAUDE.md          # this file
├── qocha.json         # engine config (owner, dirs, models)
├── index.md           # content catalog — read first on any query
├── log.md             # thin chronological index — 2-line entry per batch
├── logs/              # per-batch detail pages — type: log-detail
├── {raw}/             # IMMUTABLE — never modify, only read
└── wiki/              # agent-owned — all generated pages live here
```

**Invariant:** `{raw}/` is read-only for the agent. Never create,
rename, edit, or delete files there.

## {name}-specific rules

- **Discipline layer:** {{{{git commit-per-op, or synced log-per-op}}}}
- **Extraction commands:** {{{{one line per source filetype}}}}
- **Taxonomy:** {{{{the category tags — top-level strata}}}}
- **Junk-drawer rule:** {{{{what is skipped at ingest, no stub}}}}
- **Privacy rules:** {{{{what never enters wiki pages}}}}
- **Hub pages:** {{{{the type: topic pages that organize the corpus}}}}

## Ingest state

Forward-only: a raw file is unprocessed if no source-summary references
it. Preflight every ingest with `qocha preflight .`; postflight with
`qocha lint .`.
"""

INDEX_STARTER = """# {name} — index

The content catalog. Read first on any query; updated by every ingest.

## Ingest coverage

| Tranche | Status | Notes |
|---|---|---|
| (first tranche) | pending | plan it in CLAUDE.md |

## Pages

(catalog rows land here as ingests run)
"""

LOG_STARTER = """# {name} — log

Thin chronological index: two lines per operation, details in `logs/`.

- {today} — vault initialized by `qocha init`.
"""


def init_vault(root, name=None, raw_dir="raw"):
    """Create the missing pieces of a three-layer vault under `root`.
    Returns vault-relative paths created (empty when everything already
    existed)."""
    vault = Path(root).expanduser().resolve()
    name = name or vault.name
    created = []

    def mkdir(rel):
        p = vault / rel
        if not p.is_dir():
            p.mkdir(parents=True)
            created.append(rel + "/")

    def seed(rel, content):
        p = vault / rel
        if not p.exists():
            p.write_text(content)
            created.append(rel)

    mkdir(raw_dir)
    mkdir("wiki")
    mkdir("logs")
    today = date.today().isoformat()
    seed("CLAUDE.md", SCHEMA_STARTER.format(name=name, raw=raw_dir))
    seed("index.md", INDEX_STARTER.format(name=name))
    seed("log.md", LOG_STARTER.format(name=name, today=today))
    seed("qocha.json", json.dumps(
        {"owner": "the owner", "answer_model": "sonnet"}, indent=2) + "\n")
    return created
