# Schema starter — `CLAUDE.md` for a new vault

`qocha init` seeds a trimmed version of this into a new vault. Fill
every `{{param}}` using the [adaptation checklist](adaptation-checklist.md);
delete the variant you do not use. This file is the live spec the agent
reads at the start of every session — co-evolve it with the model as
conventions stabilize.

---

# {{VAULT_NAME}} — Schema

> **See also:** the qocha wiki spec (`conventions/wiki-spec.md` in the
> qocha repo) — this vault extends that foundation (three-layer
> pattern, ingest/query/lint/clean operations, density ladder,
> frontmatter shape). Everything below adds {{VAULT_NAME}}-specific
> rules.

## Purpose

{{CORPUS_DESCRIPTION — what this vault is, whose knowledge it holds,
whether sources are a live intake stream or a fixed historical
archive. The wiki compounds through successive ingest tranches and
later synthesis passes.}}

## Directory layout

```
{{VAULT_NAME}}/
├── CLAUDE.md          # this file
├── qocha.json         # engine config (owner, dirs, models)
├── index.md           # content catalog — read first on any query
├── log.md             # thin chronological index — 2-line entry per batch
├── logs/              # per-batch detail pages — type: log-detail
├── {{RAW_DIR}}/       # IMMUTABLE — never modify, only read
└── wiki/              # agent-owned — all generated pages live here
```

**Invariant:** `{{RAW_DIR}}/` is read-only for the agent. Never create,
rename, edit, or delete files there.

## {{VAULT_NAME}}-specific rules

- **Discipline layer:** {{PICK ONE:
    GIT VARIANT — this vault is a git repo; one commit per operation,
    prefixes per the wiki spec, push after committing.
    NO-GIT VARIANT — this vault is synced by {{SYNC_SERVICE}}; every
    operation gets its `log.md` entry plus a `logs/` detail page.}}
- **Extraction commands.** {{EXTRACTION_TABLE — one line per source
    filetype, e.g.:
    `.doc`/`.docx` -> `textutil -convert txt -stdout <file>` (macOS)
    `.pdf` -> `pdftotext <file> -`
    images -> multimodal Read
    legacy formats and audio -> defer and log}}
- **Taxonomy.** Every source-summary carries exactly one category tag
  from: {{CATEGORY_TAGS — the top-level strata of this corpus}}.
  Content tags follow the universal tag policy.
- **Slug collisions.** Slug = kebab-case of the filename (sans
  extension); on collision or over-generic names, prefix with the
  category or a content-derived word. The `source:` link stays
  byte-for-byte exact regardless of slug.
- **Junk-drawer rule.** {{JUNK_RULES — what counts as a non-source in
  this corpus and is skipped at ingest with no stub. Triage by file,
  not only by folder — real documents inside a junk drawer are still
  sources.}}
- **Duplicate detection.** Near-identical extracted text does not get a
  second summary; add the duplicate path to the existing page under a
  `> Duplicate copies:` note.
- **Privacy rules.** {{PRIVACY_LINES — for financial/medical/personal
  corpora, what NEVER enters wiki pages (amounts, balances,
  diagnoses).}}
- **Hub pages.** {{HUB_PLAN — the type: topic pages that organize
  source-summaries, usually one per category tag; created on the first
  ingest, extended after.}}

## Ingest state

Forward-only: a raw file is unprocessed if no source-summary references
it. Tranche status lives in `index.md` under "Ingest coverage".
Preflight every ingest with `qocha preflight .`; postflight with
`qocha lint .`.
