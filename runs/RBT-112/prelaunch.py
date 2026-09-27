"""RBT-112: the pre-launch verdict on the per-arm controls (prelaunch.sh; PREREGISTRATION.md §6.3).

Reads controls/prelaunch-{rbt102,pc,resting}-HZ-{801,4}.txt (the arm's own S = 0 hosts, 61-season smoke runs,
seven bodies) and the S = 0 no-selection tables, and prints:
  (a) analyse.py's positive control on each smoke run: PASSED / FAILED;
  (b) the install control (function.py --install 32, the readout's usability control): the line's call, and the
      per-body pass rate (bodies whose installed-compass F > 0);
  (c) F12's resting drive on the frozen-bias arm: faults (a paying carrier whose planted-unit bias is not 0);
  (d) the HELD call by construction: at each depth, the S = 0 table's mu and the binomial bound B (RBT-104
      peek.binom_q95, held.py's) for n = 10, 20 and 40 planted-rooted living, and whether k_planted = n
      (every planted-rooted genome paying) exceeds B, i.e. whether HELD CAN fire there.
PRELAUNCH: PASS iff (a) passes and (b) reads FOOD-DEPENDENT on both seeds, (c) shows no fault, and (d) shows
HELD reachable at n = 20 at every depth 2..40 on all ten seeds.  (Depths 0-1 cannot be HELD by any arm:
there the operator alone keeps >= 92% of lineages paying.  No reading is taken there: the window is deeper.)

Usage: prelaunch.py > controls/prelaunch.txt
"""
import importlib.util
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt104_peek_pl", os.path.join(_ROOT, "runs", "RBT-104", "peek.py"))
peek = importlib.util.module_from_spec(_spec)
sys.modules["rbt104_peek_pl"] = peek
_spec.loader.exec_module(peek)

C = os.path.join(_HERE, "controls")
SMOKE_SEEDS = (801, 4)
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
DEPTHS = (1, 2, 4, 8, 12, 16, 20, 25, 30, 40)


def s0_table(seed):
    head, p = None, {}
    for line in open(os.path.join(_HERE, "baseline", f"baseline-w32-S0-{seed}.txt")):
        if line.startswith("# depth"):
            head = line[2:].strip().split("\t")
        elif not line.startswith("#"):
            r = dict(zip(head, line.split()))
            p[int(r["depth"])] = float(r["pay32_frac"])
    return p


def main():
    print("# RBT-112 pre-launch controls on the arm's own S = 0 hosts (HZ smoke runs, 61 seasons, bests 0..60; not arms)\n")
    ok = True
    for s in SMOKE_SEEDS:
        txt = open(os.path.join(C, f"prelaunch-rbt102-HZ-{s}.txt")).read()
        m = re.search(r"^SUMMARY (\{.*\})$", txt, re.M)
        summ = json.loads(m.group(1)) if m else {}
        pc102 = bool(summ.get("pc_pass"))
        pc = open(os.path.join(C, f"prelaunch-pc-HZ-{s}.txt")).read()
        line = re.search(r"^LINE \S+: (.*)$", pc, re.M)
        fd = bool(line) and line.group(1).startswith("FOOD-DEPENDENT")
        bodies = [float(x) for x in re.findall(r"^g\d+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+\|\s+([+-][\d.]+)", pc, re.M)]
        rest = open(os.path.join(C, f"prelaunch-resting-HZ-{s}.txt")).read()
        rl = re.search(r"^RESTING .*$", rest, re.M)
        faults = int(re.search(r"frozen-bias faults (\d+)", rest).group(1)) if re.search(r"frozen-bias faults (\d+)", rest) else -1
        print(f"seed {s}:")
        print(f"  (a) analyse.py positive control: {'PASSED' if pc102 else 'FAILED'} ({summ.get('pc_detected')}/{summ.get('pc_total')})")
        print(f"  (b) install control, the line: {line.group(1) if line else 'missing'}")
        print(f"      per body, installed-compass F > 0: {sum(b > 0 for b in bodies)} of {len(bodies)} "
              f"({', '.join(f'{b:+.3f}' for b in bodies)})")
        print(f"  (c) {rl.group(0) if rl else 'resting: missing'}")
        ok &= pc102 and fd and faults == 0
    print("\n(d) HELD by construction on the S = 0 tables: B = binom_q95(n, mu(d)); HELD can fire iff n > B (k_planted <= n)")
    print("| seed | " + " | ".join(f"d {d}: mu, B10/B20/B40" for d in DEPTHS) + " |")
    print("|---|" + "---|" * len(DEPTHS))
    reach = True
    for s in SEEDS:
        p = s0_table(s)
        cells = []
        for d in DEPTHS:
            B = [peek.binom_q95(n, p[d]) for n in (10, 20, 40)]
            cells.append(f"{p[d]:.3f}, {B[0]}/{B[1]}/{B[2]}")
            if d >= 2:
                reach &= 20 > B[1]
        print(f"| {s} | " + " | ".join(cells) + " |")
    print(f"HELD reachable at n = 20 at every depth 2..40 on all ten seeds: {'YES' if reach else 'NO'}")
    ok &= reach
    import subprocess
    tree = subprocess.run(["git", "rev-parse", "HEAD:rabbitstew"], cwd=_ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "rabbitstew"], cwd=_ROOT, capture_output=True, text=True).stdout.strip()
    print(f"\nrabbitstew_tree {tree}{' (DIRTY: not a valid record)' if dirty else ''}")
    print(f"PRELAUNCH: {'PASS' if ok and not dirty else 'FAIL'}")


if __name__ == "__main__":
    main()
