"""Background maintainer: incremental rescan + vector fill on a timer.

Library consumers embed this in their own process; the CLI's --watch flag
runs it in the foreground. Dormant (cheap no-op ticks) when the vault
root does not exist, and it never dies on an indexing error.
"""
import threading
import time

RESCAN_S = 300


class Indexer(threading.Thread):
    def __init__(self, vault, interval=RESCAN_S, startup_delay=5):
        super().__init__(daemon=True, name="qocha-indexer")
        self.vault = vault
        self.interval = interval
        self.startup_delay = startup_delay
        self._stop = threading.Event()

    def run(self):
        time.sleep(self.startup_delay)
        while not self._stop.is_set():
            try:
                self.vault.scan()
                self.vault.embed_pending()
            except Exception:  # noqa: BLE001 — the indexer never dies
                pass
            self._stop.wait(self.interval)

    def stop(self):
        self._stop.set()
