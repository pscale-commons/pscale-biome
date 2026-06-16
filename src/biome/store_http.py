"""store_http — another biome's wire door as a storage adapter (storage 1.5).

The same membrane FsStore offers — load_block, save_block, list_blocks —
spoken over a remote biome-beach door. This is how one form acts on a
remote commons: the mind authors into it, related surfaces sync with it.
Writes travel as spark writes through the door, so the remote membrane
judges them like any guest's.
"""

import json
import urllib.request


class HttpStore:
    def __init__(self, origin, timeout=15):
        self.origin = origin.rstrip("/")
        self.door = self.origin + "/.well-known/biome-beach"
        self.timeout = timeout

    def _request(self, url, payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    def load_block(self, name):
        try:
            return self._request(self.door + "?block=" + name)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise

    def save_block(self, name, block):
        self._request(self.door, {"block": name, "content": block})
        return name

    def write(self, name, number=None, attention=None, content=None):
        """A shaped spark write through the door (point/ring/directory)."""
        return self._request(self.door, {"block": name, "number": number,
                                         "attention": attention, "content": content})

    def list_blocks(self, prefix=""):
        names = self._request(self.door).get("blocks", [])
        return [n for n in names if n.startswith(prefix)]
