"""The qocha command line.

    qocha index  <root> [--db PATH] [--no-embed] [--embed-limit N] [--watch]
    qocha search <root> "query" [--db PATH] [-n N] [--json]
    qocha ask    <root> "question" [--db PATH] [-k N] [--model NAME] [--json]
    qocha status <root> [--db PATH]

The vault root may carry a qocha.json overriding defaults (dirs, owner,
db, ollama_url, embed_model, answer_model); flags win over the file.
"""
import argparse
import json
import sys
import time

from .vault import Vault


def _vault(args):
    overrides = {"db": getattr(args, "db", None)}
    if getattr(args, "model", None):
        overrides["answer_model"] = args.model
    return Vault(args.root, **overrides)


def cmd_index(args):
    v = _vault(args)
    t0 = time.time()
    out = v.scan()
    if "error" in out:
        print(out["error"], file=sys.stderr)
        return 1
    print(f"scanned {out['seen']} notes "
          f"({out['changed']} changed, {out['removed']} removed) "
          f"in {time.time() - t0:.1f}s")
    if not args.no_embed:
        t0 = time.time()
        n = v.embed_pending(limit=args.embed_limit)
        if n:
            print(f"embedded {n} chunks in {time.time() - t0:.1f}s")
        else:
            st = v.status()
            if st["vectors"] < st["chunks"]:
                print(f"embedder unreachable — {st['chunks'] - st['vectors']}"
                      " chunks pending, full-text search still works")
    if args.watch:
        print("watching (Ctrl-C to stop)")
        try:
            while True:
                time.sleep(args.interval)
                out = v.scan()
                if out.get("changed") or out.get("removed"):
                    print(f"rescan: {out['changed']} changed, "
                          f"{out['removed']} removed")
                v.embed_pending()
        except KeyboardInterrupt:
            pass
    return 0


def cmd_search(args):
    v = _vault(args)
    hits = v.search(args.query, limit=args.n)
    if args.json:
        print(json.dumps(hits, indent=1))
        return 0
    if not hits:
        print("no hits")
        return 0
    for h in hits:
        print(f"{h['path']}  ::  {h['heading']}")
        snippet = " ".join(h["text"].split())[:180]
        print(f"    {snippet}")
    return 0


def cmd_ask(args):
    v = _vault(args)
    out = v.ask(args.question, k=args.k)
    if args.json:
        print(json.dumps(out, indent=1))
        return 0
    print(out["answer"].strip())
    if out["citations"]:
        print("\nsources:")
        for c in out["citations"]:
            print(f"  [[{c['ref']}]] -> {c['path']}")
    return 0


def cmd_status(args):
    v = _vault(args)
    st = v.status()
    for k, val in st.items():
        print(f"{k:>10}: {val}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="qocha",
        description="Local-first vault engine: hybrid search and grounded, "
                    "cited answers over a folder of markdown notes.")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("root", help="vault root directory")
        sp.add_argument("--db", default=None,
                        help="index path (default <root>/.qocha/index.sqlite)")

    sp = sub.add_parser("index", help="scan the vault and fill vectors")
    common(sp)
    sp.add_argument("--no-embed", action="store_true",
                    help="scan only, skip the vector fill")
    sp.add_argument("--embed-limit", type=int, default=1_000_000,
                    help="max chunks to embed this run")
    sp.add_argument("--watch", action="store_true",
                    help="keep rescanning in the foreground")
    sp.add_argument("--interval", type=int, default=300,
                    help="rescan interval seconds with --watch")
    sp.set_defaults(fn=cmd_index)

    sp = sub.add_parser("search", help="hybrid search, ranked chunks")
    common(sp)
    sp.add_argument("query")
    sp.add_argument("-n", type=int, default=10, help="max hits")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_search)

    sp = sub.add_parser("ask", help="grounded, cited answer over the vault")
    common(sp)
    sp.add_argument("question")
    sp.add_argument("-k", type=int, default=10, help="chunks to retrieve")
    sp.add_argument("--model", default=None,
                    help="answer model (default sonnet)")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_ask)

    sp = sub.add_parser("status", help="index counts and freshness")
    common(sp)
    sp.set_defaults(fn=cmd_status)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
