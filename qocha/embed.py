"""Embedding backends.

An embedder is any object with two methods:

    embed_documents(texts) -> list of unit numpy vectors, or None
    embed_query(text)      -> one unit numpy vector, or None

None means the backend is unreachable; callers treat that as "pause and
resume later", never as an error. The default backend is a local Ollama
daemon running nomic-embed-text, whose asymmetric search prefixes
(search_document / search_query) are applied here so callers never think
about them.
"""
import json
import urllib.request

try:
    import numpy as np
except ImportError:                      # vector layer optional; FTS works
    np = None


class OllamaEmbedder:
    def __init__(self, url="http://localhost:11434",
                 model="nomic-embed-text", timeout=180):
        self.url = url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _post(self, payload):
        req = urllib.request.Request(
            self.url + "/api/embed", data=json.dumps(payload).encode(),
            headers={"content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())
        except Exception:  # noqa: BLE001 — daemon down / model missing
            return None

    def _embed(self, texts):
        if np is None:
            return None
        r = self._post({"model": self.model, "input": texts})
        if not r or "embeddings" not in r:
            return None
        out = []
        for e in r["embeddings"]:
            v = np.array(e, dtype="float32")
            out.append(v / (np.linalg.norm(v) + 1e-9))
        return out

    def embed_documents(self, texts):
        return self._embed([f"search_document: {t}"[:6000] for t in texts])

    def embed_query(self, text):
        vecs = self._embed([f"search_query: {text}"[:6000]])
        return vecs[0] if vecs else None
