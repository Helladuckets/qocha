# The three-layer pattern

Qocha's conventions target the vault architecture popularly known as
Karpathy's LLM Wiki. The pattern says take the structure and make it
your own; Qocha puts an engine in it. The structure is three layers:

```
vault/
├── raw/          # layer 1: immutable source corpus
├── wiki/         # layer 2: agent-written synthesis
└── CLAUDE.md     # layer 3: the schema you co-evolve with the model
```

## Layer 1: `raw/` — the dump folder

Everything you want the vault to know lands here: clipped articles,
PDFs, exports, images, meeting notes. Sources arrive from anywhere (the
official Obsidian Web Clipper is a good capture companion; scheduled
exports and manual saves work the same) and are **immutable from the
agent's perspective** — the agent reads raw files but never creates,
renames, edits, or deletes them. Your originals are the ground truth
the whole system can always be rebuilt from.

Two narrow exceptions, both owner-serving: tag-only frontmatter edits
at ingest (per the vault's tag policy), and soft-deletion — a `clean`
operation moves files to `pending-user-deletion/` for the owner to
hard-delete at their leisure. The agent never `rm`s a raw file.

## Layer 2: `wiki/` — the synthesis

Agent-written markdown: one summary page per source, entity and concept
pages, topic hubs, query answers. Interlinked with `[[wikilinks]]`,
fronted with a small YAML contract (see [wiki-spec.md](wiki-spec.md)).
The wiki is a **compounding artifact**: new sources update existing
pages rather than triggering re-synthesis from scratch, contradictions
get flagged instead of silently overwritten, and answers worth keeping
are filed back in as pages.

## Layer 3: the schema — `CLAUDE.md`

The vault's standing operating procedures for the model: how to ingest,
what pages to create, the taxonomy, the junk rules, the privacy lines.
The owner and the model co-evolve it — when a recurring pattern
stabilizes, it gets written into the schema. A starter lives at
[schema-template.md](schema-template.md); `qocha init` seeds one into a
new vault.

## Where Qocha fits

The pattern describes content; Qocha supplies the machinery around it:

- **The engine** (`qocha index / search / ask`) — hybrid retrieval and
  grounded, cited answers over the whole vault.
- **The harness** (`qocha lint / preflight`, plus
  [../harness/ingest-agent-prompt.md](../harness/ingest-agent-prompt.md))
  — the ingest contract for agents and the structural checks that keep
  the layers honest.
- **The scaffold** (`qocha init`) — a new three-layer vault in one
  command.

The engine works on any folder of markdown; the conventions are what
make a vault compound instead of accumulate.
