"""membrane — the identity membrane (handle-mode): the write-gate beside the
world-membrane. Reads are open (an Observer owes nothing); writing requires a
located identity — a shell — whose face covers the target block's stratum (the
CADO write-aperture). Per src/biome/identity-membrane.json.

The proof that a write holds its shell is PLUGGABLE. handle-mode (built) trusts
the signing handle — honesty among friends, no secret; verify_proof returns True
once the shell exists. lock-mode (the later crystallisation) verifies a passphrase
against the shell's stored lock; it drops into verify_proof alone, the gate
unchanged. handle-mode's known limit — a face is self-declared, so it is only as
honest as the writer — is exactly what the lock (and face-granting) will close
for a stranger-facing RPG.

OFF by default (BIOME_MEMBRANE unset) so a live beach is unaffected. Turn it on
deliberately, with a migration grace, on a fresh beach.
"""

import os

FACE_RANK = {"character": 1, "author": 2, "designer": 3}
STRATUM_MIN = {"marks": 1, "world": 2, "constitution": 3}   # least face-rank that may write it
OWN_PREFIXES = ("shell-", "surface-")


def enabled(flag=None):
    """The membrane runs only when turned on — env BIOME_MEMBRANE=on, or an
    explicit flag (tests). Off by default keeps a live beach open."""
    if flag is not None:
        return bool(flag)
    return os.environ.get("BIOME_MEMBRANE", "").lower() in ("on", "1", "true")


def shell_name(handle):
    return "shell-" + handle


def owned_by(block):
    """The handle a block belongs to, if it is an identity block (shell-/surface-)."""
    for p in OWN_PREFIXES:
        if block.startswith(p):
            return block[len(p):]
    return None


def stratum(block, constitution):
    """Which stratum a block sits in — own (an identity's), constitution
    (genome-carried), marks (the open ledger), or world (grown content)."""
    owner = owned_by(block)
    if owner:
        return "own", owner
    if block == "marks":
        return "marks", None
    if block in constitution:
        return "constitution", None
    return "world", None


def face_covers(face, st):
    return FACE_RANK.get(face, 0) >= STRATUM_MIN.get(st, 99)


def verify_proof(shell, handle, proof):
    """handle-mode: the shell existing under the handle is the proof — no secret.
    lock-mode (later) replaces this body to hash `proof` against the shell's
    stored lock; the gate calls it the same way."""
    return shell is not None


def shell_face(shell):
    """A shell declares its face at position 1; default is the narrowest
    participant, Character."""
    f = shell.get("1") if isinstance(shell, dict) else None
    return (f if isinstance(f, str) else "character").strip().lower()


def check(store, args, constitution):
    """The write-gate. Returns (ok, reason). Reads always pass; a write must be
    signed by a handle, and either write the signer's own identity (registration
    / self-authoring) or hold a registered shell whose face covers the target."""
    if not ("content" in args and args["content"] is not None):
        return True, "read"                                  # Observer reads freely

    block = args["block"]
    handle = args.get("handle")
    if not handle:
        return False, ("unlocated write — to write you must be located. Register by "
                       "writing block 'shell-<yourhandle>' (you become a Character). "
                       "Reads are open; writing needs a shell.")

    st, owner = stratum(block, constitution)

    if owner == handle:                                      # your own shell/surface — register or self-author
        existing = store.load_block(shell_name(handle))
        if existing is not None and not verify_proof(existing, handle, args.get("proof")):
            return False, "proof failed for shell-%s" % handle
        return True, "self"

    shell = store.load_block(shell_name(handle))             # any other write needs a registered shell
    if shell is None:
        return False, "register first — write block 'shell-%s' to become a Character" % handle
    if not verify_proof(shell, handle, args.get("proof")):
        return False, "proof failed for shell-%s" % handle
    if owner and owner != handle:
        return False, "block '%s' belongs to %s — not yours to write" % (block, owner)

    face = shell_face(shell)
    if not face_covers(face, st):
        return False, "your face '%s' may not write %s blocks (need %s+)" % (
            face, st, next(k for k, v in FACE_RANK.items() if v == STRATUM_MIN.get(st, 99)))
    return True, "ok"
