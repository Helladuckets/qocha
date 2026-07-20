"""Answer backends for grounded ask.

An answerer is any callable prompt -> str. The default shells out to the
Claude Code CLI (`claude --print`), which uses whatever login the machine
already has — no API key handling in this package. Retrieval is local
either way; only the retrieved excerpts and the question leave the
process, and only when ask() is actually called.
"""
import json
import os
import subprocess


def _strip_env():
    """Drop inherited model-auth variables so the CLI resolves its own
    stored login rather than a stray key from the parent process."""
    return {k: v for k, v in os.environ.items()
            if not (k.startswith("ANTHROPIC_") or k.startswith("CLAUDE"))}


class ClaudeCLI:
    def __init__(self, model="sonnet", timeout=180):
        self.model = model
        self.timeout = timeout

    def __call__(self, prompt):
        cmd = ["claude", "--print", "--output-format", "json",
               "--model", self.model]
        res = subprocess.run(cmd, input=prompt, capture_output=True,
                             text=True, timeout=self.timeout,
                             env=_strip_env())
        if res.returncode != 0:
            raise RuntimeError(
                f"claude exit {res.returncode}: {res.stderr.strip()[-400:]}")
        try:
            envelope = json.loads(res.stdout)
            text = envelope.get("result", "")
            if envelope.get("is_error"):
                raise RuntimeError(f"claude error: {text[:300]}")
        except json.JSONDecodeError:
            text = res.stdout
        return text
