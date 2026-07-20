# Wiki spec — the content contract

The rules that make a three-layer vault (see
[the-pattern.md](the-pattern.md)) lintable, navigable, and compounding.
`qocha lint` enforces the structural half of this spec; the rest is
judgment the schema file encodes per vault. The spec was extracted from
a production vault operated daily and proven portable by later
deployments; each vault's `CLAUDE.md` extends it with corpus-specific
rules.

## Page frontmatter

Every page in `wiki/` starts with:

```yaml
---
title: <human-readable title>
type: <emergent — e.g. entity, concept, topic, comparison, source-summary, query-answer>
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[source-summary-slug-1]]"
  - "[[source-summary-slug-2]]"
source_count: <int>
---
```

- Filenames are **kebab-case**; slugs must be unique across the wiki.
- Internal links use `[[wikilinks]]` (Obsidian-style).
- Frontmatter wikilink values are always **quoted YAML strings** —
  unquoted `[[...]]` parses as nested YAML flow sequences and breaks
  Obsidian's Properties pane.
- Meta page types (`building-block`, `feature`, `build-log`,
  `log-detail`, `operations-report`) are exempt from the `tags`
  requirement; their documented shapes omit it.

## The source-routing density ladder

Only **source-summary** pages link into `raw/`, via
`source: "[[Exact Raw Filename]]"` — byte-for-byte, including the
extension. Every other page's `sources:` field points at
source-summary slugs, never raw filenames:

```
synthesis page -> source-summary -> raw file
```

The agent opens a raw file only when the summary is insufficient for
the question at hand. Two legitimate ways a source-summary omits the
`source:` line: **catalog/roundup pages** (`source_count: >= 2`,
bundling N raw files via body links) and **kept orphans**
(`source_count: 0` with a "> Note: source removed" line — synthesis
retained after its raw file was cleaned).

## Tag policy

Tags describe **content**: subjects, people, products, entities,
concepts, domains — kebab-case. Tags never describe the **source
platform or file format**; platform identity belongs in `source:` (the
graph edge) and `source_type:` (the content shape). Each vault
maintains its own strip set and applies it at ingest.

## The four operations

- **Ingest** — batch-process new files in `raw/`: source-summaries,
  entity/concept updates, catalogs refreshed. Preflight with
  `qocha preflight` (dangling-edge detection), postflight with
  `qocha lint`.
- **Query** — answer a question; file standalone-value answers back as
  `wiki/<slug>.md` with `type: query-answer`.
- **Lint** — beyond the structural checks: contradictions, orphans,
  stale claims, taxonomy consolidation, missing cross-references.
  Report filed as `wiki/lint-YYYY-MM-DD.md`.
- **Clean** — owner-scoped removal of raw files, two-stage: the agent
  moves them to `pending-user-deletion/`, the owner hard-deletes.

## Discipline layer

Git-backed vaults: one commit per operation, prefixed `ingest:`,
`query:`, `lint:`, `clean:`, `schema:`, `update:`, `docs:` — never
batch unrelated changes. Sync-service vaults map the same discipline to
logs instead: every operation gets a `log.md` entry plus a
`logs/YYYY-MM-DD-<op>-<slug>.md` detail page.

## Images

`wiki/assets/<anchor-page-slug>/<descriptor>.<ext>` — content-keyed
directories (what concept), descriptive filenames (what is shown).
Filenames must be globally unique: Obsidian's `![[filename.ext]]`
resolves across the whole vault. Embed with native `![[...]]` syntax.

## Manual edits are authoritative

The owner edits the vault directly. The agent treats those edits as
authoritative — never reverts prose, restructures sections, or
"corrects" formatting on the next pass. Structural drift reconciles in
the next lint pass, as a proposal.

## Co-evolution

This spec and each vault's `CLAUDE.md` are meant to change. When a
recurring pattern stabilizes — a new operation, a frontmatter field, a
tighter workflow — the agent proposes the edit during a lint pass; the
owner approves and commits it with `schema:`.
