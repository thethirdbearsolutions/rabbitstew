"""RBT-134 lanes: completeness checks for restart-safety, and the RELAY block (runs/RBT-134/LAUNCH.md).

The RELAY block carries ONLY what the no-peek discipline allows (GO-READINESS section 3): each control's id with its
YES/NO tokens, the ids on the VOID list (never their text), the B0 reproduction checks as YES/NO, the sha256 of every
output file, and CPU / wall time.  No k, p, verdict, rate, count, table or census figure ever reaches it: tokens are
built from a fixed id pattern and the literal words YES / NO, and nothing else from a readout line is copied.

    relay.py complete-assay OUT/COND.json HEAD N_PER_POOL   -> prints complete | incomplete | stale
    relay.py complete-h1    OUT/h1-COND.json HEAD N_PER_POOL -> likewise
    relay.py relay-a OUT_DIR HEAD WALL_S CPU...              -> lane A's RELAY block
    relay.py relay-b OUT_DIR HEAD WALL_S CPU...              -> lane B's RELAY block   (CPU: bash `times`, children)
"""
import hashlib
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
E2_SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)  #: RBT-112's ten (runs/RBT-112/erasure.py)

#: the control lines the readout prints (assay.py readout), and the safe id each maps to
CONTROL = re.compile(r"^(I[1-7]) (B0|C\+|A0|P[1-5])\b")
B0_PREFIX = re.compile(r"^B0 background, first 5,000 per pool, (all|unflagged):")
VOID_IDS = (  # (pattern on a VOID list entry, safe id); anything unmatched is relayed as "OTHER"
    (re.compile(r"^I2 (B0|C\+|A0|P[1-5])\b"), "I2 {0}"),
    (re.compile(r"^I3 (B0|C\+|A0|P[1-5])$"), "I3 {0}"),
    (re.compile(r"^I4 C\+$"), "I4 C+"),
    (re.compile(r"^I5 (B0|C\+|A0|P[1-5])$"), "I5 {0}"),
    (re.compile(r"^B0 background prefix (all|unflagged)$"), "B0-background-prefix {0}"),
    (re.compile(r"^B0's own k"), "B0-own-k"),
    (re.compile(r"^(B0|C\+|A0|P[1-5]): the generalised predicate"), "predicate-mismatch {0}"),
)


def _load(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return None


def complete(path, head, n_per_pool):
    """complete: parses, covers both pools at n each, and was written at HEAD.  stale: complete but at another head
    (the lane refuses).  incomplete: anything else (the lane re-runs it)."""
    r = _load(path)
    if not r or not isinstance(r.get("pools"), dict):
        return "incomplete"
    if len(r["pools"]) != 2 or any(v != n_per_pool for v in r["pools"].values()):
        return "incomplete"
    if r.get("git", head) != head:
        return "stale"
    return "complete"


def tokens(line):
    return " ".join(re.findall(r"\b(YES|NO)\b", line)) or "NO-TOKEN"


def readout_tokens(readout):
    out, void, in_void = [], [], False
    for line in open(readout).read().splitlines():
        if line.startswith("## VOID"):
            in_void = True
            continue
        if in_void:
            if line.startswith("## "):
                in_void = False
            elif line.strip() == "none":
                void.append("none")
            elif line.startswith("- "):
                entry, safe = line[2:].strip(), "OTHER"
                for pat, fmt in VOID_IDS:
                    m = pat.match(entry)
                    if m:
                        safe = fmt.format(*m.groups())
                        break
                void.append(safe)
            continue
        m = CONTROL.match(line)
        if m:
            out.append(f"{m.group(1)} {m.group(2)}: {tokens(line)}")
            continue
        m = B0_PREFIX.match(line)
        if m:
            out.append(f"B0-background-prefix {m.group(1)}: {tokens(line)}")
    return out, void


def _floats(text):
    return [float(x) for x in re.findall(r"[-+]?\d+\.\d+|\d+", text)]


def e1_b0_matches(e1_path):
    """YES iff E1's B0 rows equal RBT-121's committed parity.txt (same four numbers, same rounding)."""
    try:
        rows = [l for l in open(e1_path).read().splitlines() if l.startswith("| B0 |")]
        ref = open(os.path.join(_ROOT, "runs", "RBT-121", "ga", "parity.txt")).read().splitlines()
    except OSError:
        return "NO"
    if len(rows) != 2:
        return "NO"
    for row, kind in zip(rows, ("holistic", "conventional")):
        want = [l for l in ref if l.startswith(kind)]
        if not want or kind not in row:
            return "NO"
        if _floats(row.split(kind, 1)[1]) != _floats(want[0].split(kind, 1)[1]):
            return "NO"
    return "YES"


def e2_b0_matches(out_dir):
    """YES iff every E2 B0 table equals RBT-112's committed baseline-w32-SEED.txt below the header."""
    for s in E2_SEEDS:
        try:
            got = open(os.path.join(out_dir, f"e2-B0-{s}.txt")).read().splitlines()[1:]
            want = open(os.path.join(_ROOT, "runs", "RBT-112", "baseline", f"baseline-w32-{s}.txt")).read().splitlines()[1:]
        except OSError:
            return "NO"
        if got != want:
            return "NO"
    return "YES"


def hashes(out_dir, names):
    lines = []
    for name in sorted(names):
        p = os.path.join(out_dir, name)
        if os.path.isfile(p):
            lines.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  runs/RBT-134/out/{name}")
    return lines


def relay(lane, out_dir, head, wall, cpu=""):
    print(f"===== RELAY RBT-134 lane {lane} =====")
    print(f"head {head}")
    if lane == "A":
        tok, void = readout_tokens(os.path.join(out_dir, "readout.txt"))
        print("TOKENS")
        for t in tok:
            print(f"  {t}")
        print("VOID " + (", ".join(void) if void else "MISSING"))
        names = [f for f in os.listdir(out_dir) if (f.endswith(".json") and not f.startswith("h1-")) or f == "readout.txt"
                 or f.endswith("-resign.txt")]
    else:
        print("TOKENS")
        print(f"  E1-B0-equals-parity.txt: {e1_b0_matches(os.path.join(out_dir, 'e1.txt'))}")
        print(f"  E2-B0-equals-RBT-112-tables: {e2_b0_matches(out_dir)}")
        names = [f for f in os.listdir(out_dir) if f.startswith(("e1", "e2-", "h1-"))]
    print("SHA256")
    for line in hashes(out_dir, names):
        print(f"  {line}")
    print(f"TIME wall_s={wall} cpu_children_user_sys={cpu}")
    print("===== END RELAY =====")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd in ("complete-assay", "complete-h1"):
        print(complete(sys.argv[2], sys.argv[3], int(sys.argv[4])))
    elif cmd == "relay-a":
        relay("A", sys.argv[2], sys.argv[3], sys.argv[4], " ".join(sys.argv[5:]))
    elif cmd == "relay-b":
        relay("B", sys.argv[2], sys.argv[3], sys.argv[4], " ".join(sys.argv[5:]))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
