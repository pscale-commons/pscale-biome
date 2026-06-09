"""sense — the biome host sensor (Layer 1 inspecting its landing).

Inspect the host the biome landed on and return a conditions report: what
storage is available, whether cognition (an LLM key) is present, what the
runtime is, what federation reach exists. The unfolder maps these conditions
onto the biome shell's seven currents to decide the biome's form.

Sensing is read-only and fast; nothing here commits a surface. A TypeScript
sensor reports the same shape for browser / KV hosts; this one is for Python
hosts (thumbdrive, laptop, VPS, the mobius desktop).
"""

import os
import socket
import sys


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


def sense_endpoints(port=3001):
    return {"port": port, "port_free": _port_free(port), "browser": False}


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


def sense(path="."):
    """The full conditions report — read-only, no surface committed."""
    return {
        "runtime": sense_runtime(),
        "storage": sense_storage(path),
        "cognition": sense_cognition(),
        "endpoints": sense_endpoints(),
        "federation": sense_federation(),
    }
