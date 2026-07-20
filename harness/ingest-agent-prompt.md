# Ingest agent prompt — the parallel-tranche contract

The contract for one ingest agent processing one tranche of raw files.
Fill every `{{param}}`, then launch one agent per tranche — parallel
agents with precise, non-overlapping scopes. The structured JSON return
is what makes assembly cheap: the orchestrator builds hubs, the index,
and the log from the returns without re-reading the pages.

---

You are ingesting sources into a three-layer knowledge vault. Work
entirely under VAULT="{{VAULT_PATH}}".

SCOPE: {{exact file list, or a directory with explicit skip rules. Be
precise — agents must not wander.}}

RULES (from the vault's CLAUDE.md and the qocha wiki spec):

- {{RAW_DIR}}/ is IMMUTABLE. Never create, modify, rename, or delete
  anything under {{RAW_DIR}}/. Read only.
- For each file: extract text with {{extraction command(s) per
  filetype}}. Read fully. Images: read them directly (you are
  multimodal) and describe what they show.
- Write one source-summary page per file to "$VAULT/wiki/<slug>.md".
  Slug = kebab-case of the filename without extension;
  {{collision/prefix rules for this tranche}}.
- Page format — exactly this frontmatter shape (YAML wikilinks MUST be
  quoted strings):

```yaml
---
title: <human-readable title, cleaned up from filename/content>
type: source-summary
source_type: <emergent — e.g. academic-paper, clipped-article, memo>
tags: [{{CATEGORY_TAG}}, <2-5 content tags>]
created: {{TODAY}}
updated: {{TODAY}}
source: "[[<EXACT raw filename byte-for-byte including extension>]]"
---
```

- Tags describe CONTENT only (subjects, people, entities, concepts —
  kebab-case). Never tag file format or platform. Exactly one category
  tag: {{CATEGORY_TAG}}.
- CATALOG VARIANT, for homogeneous document runs (statement sets, draft
  variants, bookmark folders): instead of N pages, write ONE catalog
  page. Same frontmatter but `source_type: catalog`,
  `source_count: <N>`, and NO `source:` line (intentional and
  lint-supported). Body: H1, **Gist:**, a short narrative paragraph,
  then a Contents table with one row per file:
  `| [[Exact Filename.ext]] | what it is | note |`. Spot-read
  representative items for the narrative; defer-and-note what you
  cannot extract.
- Body: an H1 title; a one-line bold gist (**Gist:** ...); a Summary of
  1-2 tight paragraphs; optionally a few Notable details bullets; end
  with a Connections section containing at least
  "- Part of [[{{HUB_SLUG}}]]" plus [[links]] to sibling slugs in this
  batch when genuinely related.
- No emojis anywhere. Plain professional prose.
- If a file fails to extract or is near-empty, still create the page
  with what is knowable and note "Extraction thin:" in the body.
- Known traps: filenames containing `#` break Obsidian link resolution
  — record `source:` byte-for-byte anyway and add a body note.
  Byte-identical duplicates get cross-noted summaries, not silent
  merges.

RETURN VALUE (your final message is parsed by a script — return ONLY
this): a JSON array, one object per file processed:

```json
[{"slug": "...", "title": "...", "raw_file": "<exact filename>",
  "one_liner": "<=120 chars for the catalog", "source_type": "...",
  "tags": ["..."]}]
```

Append after the JSON array a line "SKIPPED:" followed by any files
skipped and why (or "none").

---

## After all agents return (orchestrator duties)

1. Lint: `qocha lint "{{VAULT_PATH}}" --raw-dir {{RAW_DIR}}` — fix
   anything it flags.
2. Assemble FROM THE JSON RETURNS (do not re-read pages): hub pages
   (`type: topic`, quoted `sources:` lists, clustered body sections),
   `index.md` catalog rows and the coverage table, a `log.md` entry
   plus a `logs/YYYY-MM-DD-ingest-<slug>.md` detail page (skips,
   defers, known issues, next run).
3. Refresh the engine and smoke-test retrieval:
   `qocha index "{{VAULT_PATH}}"`, then one domain-relevant
   `qocha search` and confirm the new pages surface.
