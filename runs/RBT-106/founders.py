"""RBT-106: the seeded founders (PREREGISTRATION.md section 3).  RBT-104's construction, imported.

Two founder sets per RBT-90 part 2 seed, both built by RBT-104's `seed_founders.py` (imported, not
copied): the arm's own sixty part-2 designed-body founders, drawn exactly as the ecology draws them
(`seed_founders.part2_ecology` asserts the config equals the committed part-2 one), with RBT-97's
routed motif installed in the even-i half (15 at sign +1, i % 4 == 0; 15 at sign -1, i % 4 == 2),
drawn ages kept.

  w = 1    RBT-104's founders, byte for byte (the files RBT-104's S1 and S8 load).  The motif's
           linear gain is a = 2: sub-paying, inside drift's own range.  This script does not build
           them; it calls `seed_founders.write` and then checks the digest against RBT-104's
           committed `founders-digests.txt`.
  w = 32   the same founders with the motif at output w = 32 (a = 64), the rung at which RBT-103
           measured the prize.  A PAYING compass at founding, at the default link reach.  Built
           by `seed_founders.seeded` with its module constant W set to 32 for the call, so that the
           construction is RBT-104's line for line and differs in the one number.

Writes OUT/conventional/NNN.json and OUT/SHA256SUMS as `seed_founders.write` does; the digest of
SHA256SUMS is checked against `founders-digests.txt` beside this script (w = 32) or RBT-104's
(w = 1) unless --record is given (used once, to make the committed file).

Usage: founders.py SEED W OUT [--record]
"""
import hashlib
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt104_seed_founders", os.path.join(_ROOT, "runs", "RBT-104", "seed_founders.py"))
sf = importlib.util.module_from_spec(_spec)
sys.modules["rbt104_seed_founders"] = sf
_spec.loader.exec_module(sf)

DIGESTS = {1.0: os.path.join(_ROOT, "runs", "RBT-104", "founders-digests.txt"),
           32.0: os.path.join(_HERE, "founders-digests.txt")}


def digest_of(outdir):
    return hashlib.sha256(open(os.path.join(outdir, "SHA256SUMS"), "rb").read()).hexdigest()


def committed(w):
    out = {}
    for line in open(DIGESTS[w]):
        if line.strip() and not line.startswith("#"):
            s, d = line.split()
            out[int(s)] = d
    return out


def seeded(seed, w):
    """RBT-104's `seeded(seed)` with its motif weight set to w for the call."""
    old = sf.W
    sf.W = float(w)
    try:
        return sf.seeded(seed)
    finally:
        sf.W = old


def write(seed, w, outdir):
    old = sf.W
    sf.W = float(w)
    try:
        return sf.write(seed, outdir)
    finally:
        sf.W = old


if __name__ == "__main__":
    seed, w, outdir = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    if w not in DIGESTS:
        sys.exit(f"w must be 1 or 32 (the two pre-registered founder sets), not {w:g}")
    write(seed, w, outdir)
    d = digest_of(outdir)
    print(f"seed {seed}: 60 founders in {outdir}, 30 carrying the routed motif at w = {w:g} "
          f"(a = {2 * w:g}; 15 at +1, 15 at -1); SHA256SUMS digest {d}")
    if "--record" not in sys.argv:
        want = committed(w).get(seed)
        if want != d:
            sys.exit(f"DIGEST MISMATCH for seed {seed}, w = {w:g}: {d} != committed {want}")
        print("digest matches the committed one")
