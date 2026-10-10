"""RBT-134 lanes: completeness checks for restart-safety, the control gate, and the RELAY block (runs/RBT-134/LAUNCH.md).

The RELAY block carries ONLY what the no-peek discipline allows (GO-READINESS section 3): the GO sha, each control's id
with its YES/NO tokens, the ids on the VOID list (never their text), the B0 reproduction checks as YES/NO, whether the
outputs were committed, the sha256 of every output file, and per-stage wall / CPU time rounded to the hour (a finer
time could encode a count, e.g. of re-signed arrivals).  No k, p, verdict, rate, count, table or census figure ever
reaches it: tokens are built from a fixed id pattern and the literal words YES / NO, and nothing else from a readout
line is copied.

    relay.py complete-assay OUT/COND.json HEAD N_PER_POOL N_BG_PER_POOL -> complete | incomplete | stale
    relay.py complete-h1    OUT/h1-COND.json HEAD N_PER_POOL           -> likewise
    relay.py gate READOUT                                    -> PASS iff its VOID list is "none", else STOP
    relay.py founders-ok DIR SEED                            -> ok iff DIR holds RBT-106's committed w = 32 founders
    relay.py relay LANE OUT_DIR HEAD --committed yes|no --status S [NAME:WALL_S:CPU_S ...]  -> the RELAY block
"""
import argparse
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


_ASSAY = []


def _conditions():
    """assay.CONDITIONS, imported (not copied) so the check cannot drift from what `run` records."""
    if not _ASSAY:
        import importlib.util
        path = os.path.join(_ROOT, "runs", "RBT-134", "assay.py")
        spec = importlib.util.spec_from_file_location("assay134_relay", path)
        mod = importlib.util.module_from_spec(spec)
        argv, sys.argv = sys.argv, [path]
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.argv = argv
        _ASSAY.append(mod)
    return _ASSAY[0].CONDITIONS


def _cond_of(path):
    name = os.path.basename(path)
    if not name.endswith(".json"):
        return None
    return name[:-5][3:] if name.startswith("h1-") else name[:-5]


def complete(path, head, n_per_pool, n_bg_per_pool=None):
    """complete: parses, is the file's own condition, covers both pools at n each (and, for the assay, n_bg per pool
    and the condition's registered fields), and was written at HEAD.  stale: complete but written at another head, or
    recording no head (the lane refuses).  incomplete: anything else (the lane re-runs it).  The assay is told apart
    by n_bg_per_pool being given."""
    r, cond = _load(path), _cond_of(path)
    if not isinstance(r, dict) or not isinstance(r.get("pools"), dict) or r.get("condition") != cond:
        return "incomplete"
    if len(r["pools"]) != 2 or any(v != n_per_pool for v in r["pools"].values()) or r.get("n_per_pool") != n_per_pool:
        return "incomplete"
    if n_bg_per_pool is not None:
        fields = _conditions().get(cond)
        if fields is None or r.get("n_bg_per_pool") != n_bg_per_pool or r.get("fields") != json.loads(json.dumps(fields)):
            return "incomplete"
    if r.get("git") != head:
        return "stale"
    return "complete"


def gate(readout):
    """DESIGN.md 13 step 3 (I1-I7 must pass before step 4): PASS iff the readout's VOID list is exactly "none"."""
    try:
        _, void = readout_tokens(readout)
    except OSError:
        return "STOP"
    return "PASS" if void == ["none"] else "STOP"


def founders_ok(outdir, seed):
    """ok iff OUTDIR/SHA256SUMS's digest (founders.digest_of) is RBT-106's committed w = 32 digest for SEED and every
    file it lists exists and hashes as listed; else no (the lane removes the directory and rebuilds it)."""
    sums = os.path.join(outdir, "SHA256SUMS")
    try:
        digest = hashlib.sha256(open(sums, "rb").read()).hexdigest()
        want = {}
        for line in open(os.path.join(_ROOT, "runs", "RBT-106", "founders-digests.txt")):
            if line.strip() and not line.startswith("#"):
                s, d = line.split()
                want[int(s)] = d
        if digest != want.get(int(seed)):
            return "no"
        lines = [l for l in open(sums).read().splitlines() if l.strip()]
        for line in lines:
            h, name = line.split("  ", 1)
            if hashlib.sha256(open(os.path.join(outdir, name), "rb").read()).hexdigest() != h:
                return "no"
    except (OSError, ValueError):
        return "no"
    return "ok" if lines else "no"


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


def hours(seconds):
    return int(int(seconds) / 3600 + 0.5)


def relay(lane, out_dir, head, committed="no", status="done", stages=()):
    print(f"===== RELAY RBT-134 lane {lane} =====")
    print(f"head {head} (the GO sha)")
    print(f"status {status}")
    print("COMMITTED yes" if committed == "yes" else "NOT COMMITTED (RBT134_NO_PUSH=1 or no push): outputs only under runs/RBT-134/out/")
    if lane == "A":
        readout = "readout.txt" if status == "done" else "readout-controls.txt"
        tok, void = readout_tokens(os.path.join(out_dir, readout)) if os.path.exists(os.path.join(out_dir, readout)) else ([], [])
        print(f"TOKENS ({readout})")
        for t in tok:
            print(f"  {t}")
        print("VOID " + (", ".join(void) if void else "MISSING"))
        names = [f for f in os.listdir(out_dir) if (f.endswith(".json") and not f.startswith("h1-"))
                 or f.startswith("readout") and f.endswith(".txt") or f.endswith("-resign.txt") or f == "lane-A.log"]
    else:
        print("TOKENS")
        print(f"  E1-B0-equals-parity.txt: {e1_b0_matches(os.path.join(out_dir, 'e1.txt'))}")
        print(f"  E2-B0-equals-RBT-112-tables: {e2_b0_matches(out_dir)}")
        names = [f for f in os.listdir(out_dir) if f.startswith(("e1", "e2-", "h1-")) and not f.endswith((".head", ".tmp"))
                 or f == "lane-B.log"]
    print("SHA256")
    for line in hashes(out_dir, names):
        print(f"  {line}")
    for st in stages:
        name, wall, cpu = st.rsplit(":", 2)
        print(f"TIME {name} wall_h={hours(wall)} cpu_h={hours(cpu)}")
    print("===== END RELAY =====")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "complete-assay":
        print(complete(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])))
    elif cmd == "complete-h1":
        print(complete(sys.argv[2], sys.argv[3], int(sys.argv[4])))
    elif cmd == "gate":
        print(gate(sys.argv[2]))
    elif cmd == "founders-ok":
        print(founders_ok(sys.argv[2], sys.argv[3]))
    elif cmd == "relay":
        ap = argparse.ArgumentParser(prog="relay.py relay")
        ap.add_argument("lane", choices=("A", "B"))
        ap.add_argument("out_dir")
        ap.add_argument("head")
        ap.add_argument("--committed", default="no")
        ap.add_argument("--status", default="done")
        ap.add_argument("stages", nargs="*")
        a = ap.parse_intermixed_args(sys.argv[2:])
        relay(a.lane, a.out_dir, a.head, a.committed, a.status, a.stages)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
