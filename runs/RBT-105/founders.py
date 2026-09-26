"""RBT-105: the founders' fingerprint of one ecology run, so "the same founders at season 0" is a byte test.

A founder's genome file (``KIND/genomes/h0-*.json`` or ``c0-*.json``) is written once, at season 0, and carries
its genotype, its name and its staggered age (``record.age``), which are everything RBT-95's per-fauna stream
draws for it.  The fingerprint is the SHA-256 of those files, sorted by name, per fauna.

    python runs/RBT-105/founders.py RUN_DIR [LABEL]     ->  one line: LABEL holistic <sha> <n> conventional <sha> <n>

``founders-rbt90.txt`` holds the lines for the RBT-90 part 2 arms, computed from their checkpoints
(``scripts/durable.sh restore``: the bulk resumes intact, README rule 6; genomes are written once at birth).
"""
import hashlib
import pathlib
import sys


def fingerprint(run, kind):
    prefix = "h0-" if kind == "holistic" else "c0-"
    files = sorted((pathlib.Path(run) / kind / "genomes").glob(f"{prefix}*.json"), key=lambda p: p.name)
    h = hashlib.sha256()
    for p in files:
        h.update(p.name.encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest(), len(files)


def line(run, label=None):
    parts = [label or str(run)]
    for kind in ("holistic", "conventional"):
        sha, n = fingerprint(run, kind)
        parts += [kind, sha, str(n)]
    return " ".join(parts)


if __name__ == "__main__":
    print(line(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
