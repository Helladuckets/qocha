# Adaptation checklist

One pass of owner decisions per new vault; the schema template and the
harness consume the answers. Do the corpus survey before writing any
rules.

## Identity

- [ ] **Vault name and path.** If it lives inside a sync service
  (Google Drive, OneDrive), note it — that decides the discipline
  layer.
- [ ] Run `qocha init <vault>` — creates the missing layers (`raw/`,
  `wiki/`, `logs/`), seeds `CLAUDE.md`, `index.md`, `log.md`, and
  `qocha.json`, and never touches anything that already exists.

## Corpus survey (before any rules)

- [ ] Inventory by extension and folder:
  `find <RAW> -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn`
- [ ] **Raw dir name** — keep whatever the corpus already uses
  (`raw/`, `RAW/`, `sources/`). Never rename the owner's corpus dir;
  pass `--raw-dir` to the harness commands instead.
- [ ] **Signal vs junk** — which folders are real sources, which are
  junk drawers (saved-webpage `*_files/` mirrors, `.tmp`, `~$*` lock
  files, duplicate nested trees). Write the junk-drawer rule.
- [ ] **Tranche plan** — what the first ingest covers, what defers.
  Goes in `index.md` under "Ingest coverage".

## Rules (into the schema)

- [ ] **Discipline layer**: git (commit-per-op) or synced/no-git
  (log-per-op).
- [ ] **Category taxonomy**: the top-level strata, one `cat/<x>` tag
  each.
- [ ] **Extraction table**: a command per filetype present.
- [ ] **Density plan**: which clusters get individual summaries vs a
  single catalog page (statement sets, draft variants, bookmark
  folders -> catalog).
- [ ] **Privacy rules**: what never enters wiki pages.
- [ ] **Slug conventions** and collision policy.
- [ ] **Hub plan**: the `type: topic` pages that organize the corpus.

## Capture (optional but recommended)

- [ ] Point a capture tool at `raw/` — the official Obsidian Web
  Clipper saves articles as markdown directly into the vault; scheduled
  exports and manual saves work identically. Qocha ships the receiving
  conventions, not the capture tools.

## First-session checklist

1. `qocha init <vault>` run; schema and index instantiated from the
   templates.
2. First ingest run per
   [../harness/ingest-agent-prompt.md](../harness/ingest-agent-prompt.md).
3. `qocha lint <vault>` clean; `qocha preflight <vault>` clean.
4. `qocha index <vault>` built; one domain-relevant
   `qocha search` returns the right pages.
5. The owner can navigate hub -> summary -> raw in Obsidian's graph.
