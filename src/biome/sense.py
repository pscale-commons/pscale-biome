"""sense — the biome host sensor (Layer 1 inspecting its landing).

Inspect the host the biome landed on and return a conditions report: what
storage is available, whether cognition (an LLM key) is present, what the
runtime is, what federation reach exists. The unfolder maps these conditions
onto the biome shell's seven currents to decide the biome's form.

Sensing is read-only and fast; nothing here commits a surface. A TypeScript
sensor reports the same shape for browser / KV hosts; this one is for Python
hosts (thumbdrive, laptop, VPS, the mobius desktop).
"""

import json
import os
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
import spark


def _first_env(*names):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return None


def _port_free(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def sense_runtime():
    # This is the Python spark; a TS sensor reports "node" or "browser".
    return "python %d.%d" % (sys.version_info[0], sys.version_info[1])


def sense_storage(path="."):
    writable = os.access(path, os.W_OK)
    return {
        "filesystem_writable": writable,
        "fs_path": os.path.abspath(path) if writable else None,
        "hosted_db": _first_env("DATABASE_URL", "SUPABASE_URL", "PGURI"),
        "upstream_beach": _first_env("DEFAULT_BEACH", "BEACH_URL"),
    }


def sense_cognition():
    return {
        "llm_key": bool(_first_env("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "LLM_API_KEY")),
        "interactive_tty": sys.stdin.isatty(),
    }


def sense_endpoints(port=3210):
    return {"port": port, "port_free": _port_free(port), "browser": False}


def _removable(path):
    """A surface that travels: mounted volumes on darwin, media mounts on linux."""
    p = os.path.abspath(path)
    if sys.platform == "darwin":
        return p.startswith("/Volumes/")
    return p.startswith(("/media/", "/mnt/", "/run/media/"))


def sense_capacity(path="."):
    try:
        import shutil
        du = shutil.disk_usage(path)
        total, free = round(du.total / 1e9, 1), round(du.free / 1e9, 1)
    except OSError:
        total = free = None
    return {"disk_total_gb": total, "disk_free_gb": free, "removable": _removable(path)}


# --- neighbours ---------------------------------------------------------------

def _read_instance(d):
    """If the directory holds a biome instance, read its self-description through
    spark. Activated: blocks/biome.json (the becoming). Dormant: a cut genome
    (sentinel/ztone/biome.json) that has not unfolded yet. Agent: a shell of
    pscale blocks (the mobius shape). Returns a neighbour entry, or None."""
    becoming = os.path.join(d, "blocks", "biome.json")
    genome = os.path.join(d, "sentinel", "ztone", "biome.json")
    shell_dir = os.path.join(d, "shell")
    try:
        if os.path.isfile(becoming):
            block = spark.load(becoming)
            return {"kind": "biome", "state": "activated", "path": d,
                    "voicing": spark.voice(block),
                    "runtime": spark.spark(block, "1", 0).get("text"),
                    "intention": spark.spark(block, "9", 0).get("text")}
        if os.path.isfile(genome):
            return {"kind": "biome", "state": "dormant", "path": d,
                    "voicing": spark.voice(spark.load(genome))}
        if os.path.isdir(shell_dir):
            names = set(os.listdir(shell_dir))
            if {"reflexive.json", "purpose.json"} & names:
                return {"kind": "agent", "state": "shelled", "path": d,
                        "blocks": sorted(n[:-5] for n in names if n.endswith(".json"))}
    except (OSError, ValueError):
        pass
    return None


def _local_candidates(root):
    """Bounded scan: siblings of the biome's own root, the desktop run
    convention, mounted volumes (and their biome-runs), watched paths from env."""
    own = os.path.realpath(root)
    seen, dirs = set(), []

    def add(d):
        if not os.path.isdir(d):
            return
        r = os.path.realpath(d)
        if r != own and r not in seen:
            seen.add(r)
            dirs.append(d)

    parent = os.path.dirname(own)
    for ledge in [parent, os.path.expanduser("~/Desktop/biome-runs"), "/Volumes"]:
        try:
            for n in sorted(os.listdir(ledge)):
                child = os.path.join(ledge, n)
                add(child)
                runs = os.path.join(child, "biome", "biome-runs")
                if ledge == "/Volumes" and os.path.isdir(runs):
                    for v in sorted(os.listdir(runs)):
                        add(os.path.join(runs, v))
        except OSError:
            pass
    for p in (_first_env("WATCHED_PATHS") or "").split(":"):
        if p:
            add(os.path.expanduser(p))
    return dirs


def _probe_beach(host, timeout=1.5):
    """Ask a host which world it speaks, knocking the ztone door first and the
    legacy door second. One small GET per door; every failure reads as silence.
    The key-shape of what answers settles the world either way."""
    import urllib.request
    for door in ("ztone-beach", "pscale-beach"):
        url = "https://%s/.well-known/%s?block=marks" % (host, door)
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                block = json.loads(r.read().decode("utf-8"))
        except Exception:
            continue
        if not isinstance(block, dict):
            continue
        world = "legacy" if "_" in block else "ztone" if "0" in block else "unknown"
        return {"kind": "beach", "url": "https://" + host, "door": door, "world": world}
    return None


def sense_neighbours(root=".", hosts=("beach.happyseaurchin.com",), network=True):
    """Other instances this biome can reach: local biomes and agent shells found
    on nearby surfaces, and beaches that answer over the network. Detection is
    reading — a neighbour's identity is its own becoming-block."""
    found = []
    for d in _local_candidates(root):
        entry = _read_instance(d)
        if entry:
            found.append(entry)
    if network:
        watched = [h.strip().replace("https://", "").rstrip("/")
                   for h in (_first_env("WATCHED_BEACHES") or "").replace(",", " ").split()]
        for h in list(hosts) + [w for w in watched if w not in hosts]:
            entry = _probe_beach(h)
            if entry:
                found.append(entry)
    return found


def sense_federation(hosts=("beach.happyseaurchin.com",), timeout=1.5):
    reachable = []
    prev = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        for h in hosts:
            try:
                socket.getaddrinfo(h, 443)
                reachable.append(h)
            except OSError:
                pass
    finally:
        socket.setdefaulttimeout(prev)
    return {"reachable_beaches": reachable, "watched": _first_env("WATCHED_BEACHES")}


def sense(path=".", network=True):
    """The full conditions report — read-only, no surface committed."""
    return {
        "runtime": sense_runtime(),
        "storage": sense_storage(path),
        "capacity": sense_capacity(path),
        "cognition": sense_cognition(),
        "endpoints": sense_endpoints(),
        "federation": sense_federation() if network else
                      {"reachable_beaches": [], "watched": None},
        "neighbours": sense_neighbours(path, network=network),
    }
