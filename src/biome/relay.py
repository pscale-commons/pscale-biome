"""relay — the biome's own vapour relay (endpoints 3.4, server-owned).

The interface's ephemeral channel: the live presence and typing-state shared
among the humans co-present at one frame. Out-of-band from the durable
substrate — vapour is forming, not settled; it never becomes a block, never
touches the membrane, never persists. Liquid and solid commit through the door
as 0-9 blocks; only vapour rides here, and it evaporates. (shell 3.4:
"websocket, SSE, or blob-poll" — this is blob-poll, the server's own: no
Supabase, no socket.)

Frame-scoped: humans sharing a frame (a scene, an address) see one another's
vapour; humans at other frames do not. The register also knows its LOAD — the
live count across every frame — and ADVERTISES a capacity it does not enforce:
when the load reaches the cap it says `saturated`, and that signal is what the
unfolder reads to point a newcomer at a neighbour's face, or to raise another
(endpoints 3.3/3.4 unfold by condition, not configuration; a saturated face is
a condition). The relay never refuses a human — it only tells the truth about
how crowded it is.

In-memory and thread-safe: one Relay instance is shared across the serving
threads. Process-global by nature — vapour belongs to the running server, not
the disk.
"""

import threading
import time

STALE_S = 30.0          # a heartbeat older than this has gone (left, or closed the tab)
CAP = 24                # live inhabitants this relay serves before it calls itself full


class Relay:
    def __init__(self, cap=CAP, stale_s=STALE_S, clock=time.time):
        self._frames = {}                    # frame -> {handle: {"vapour","face","ts"}}
        self._lock = threading.Lock()
        self.cap = cap
        self.stale_s = stale_s
        self._clock = clock

    def beat(self, frame, handle, vapour="", face="observer"):
        """A co-present human heartbeats and shares its current vapour (its
        unsent draft). Upsert + stamp; returns this frame's live view."""
        with self._lock:
            self._frames.setdefault(frame, {})[handle] = {
                "vapour": vapour, "face": face, "ts": self._clock()}
            return self._view(frame, exclude=None)

    def view(self, frame, exclude=None):
        """Who is co-present at `frame`, their live vapour, and the server's
        load. `exclude` drops one handle (you need not be shown your own draft)."""
        with self._lock:
            return self._view(frame, exclude)

    def depart(self, frame, handle):
        """A clean leave — drop a handle now rather than wait for it to go stale."""
        with self._lock:
            f = self._frames.get(frame)
            if f:
                f.pop(handle, None)
                if not f:
                    self._frames.pop(frame, None)

    def load(self):
        """The live count across every frame — the capacity signal the unfolder
        reads. Prunes the stale as a side effect."""
        with self._lock:
            return self._view("", exclude=None)["load"]

    # --- internals: call under the lock -------------------------------------

    def _view(self, frame, exclude):
        now, total = self._clock(), 0
        for fr, f in list(self._frames.items()):           # prune every frame as we read
            for h in [h for h, v in f.items() if now - v["ts"] > self.stale_s]:
                del f[h]
            if f:
                total += len(f)
            else:
                del self._frames[fr]
        here = self._frames.get(frame, {})
        present = [{"handle": h, "face": v["face"], "vapour": v["vapour"],
                    "age": round(now - v["ts"], 1)}
                   for h, v in here.items() if h != exclude]
        return {"frame": frame, "present": present, "here": len(here),
                "load": total, "cap": self.cap, "saturated": total >= self.cap}
