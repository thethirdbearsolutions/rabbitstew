"""Adversary checks on RBT-71 Deliverable A (named adversary: the RBT-63/64 delegate).

Three questions, all answerable from committed files alone -- which is itself the point of
check 1.

1. REPRODUCIBILITY. Can the scorecard be re-derived from the repository? Runs measure.py
   against the checkout and diffs it against the committed readout -- then perturbs one
   input cell to prove that agreement is a derivation and not a replay.
2. INTERNAL CONSISTENCY. Does REPORT.md's scorecard match the committed readouts, number for
   number, on all three seeds?
3. WHAT R2 CERTIFIES. R2 is "holistic lifetime-yield heritability >= 0.20, n >= 30". The
   paired NEUTRAL controls are drift populations with no selection at all. Do any of them
   clear the same bar? If they do, R2 certifies that lifetime yield is a heritable
   measurement -- which is what the report says it tests -- and not that selection produced
   the heritability.

No simulation. Usage: adversary.py
"""

import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = "runs/RBT-71"
SEEDS = (804, 805, 806)
BULK = ("history.json", "lineage.jsonl")          # regenerable output, deliberately not committed
SUMMARY = ("seasons.txt", "lineage-last.txt")     # the argument, committed (RBT-68's rule)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root: this file is runs/RBT-71/adversary.py


def line_delta(got, want):
    """(changed-line count, a few descriptions) between two texts.

    difflib rather than a positional zip: the defect this check exists for DROPPED three
    lines, and a positional comparison would count every line after them as changed too
    (58 rather than 4), overstating a real finding. An adversary check that inflates is as
    broken as one that misses.
    """
    a, b = got.splitlines(), want.splitlines()
    n, where = 0, []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag == "equal":
            continue
        n += max(i2 - i1, j2 - j1)
        if len(where) < 4:
            where.append(f"{tag} at readout line {j1 + 1}")
    return n, where


def run_measure(cwd):
    """measure.py's stdout for the three seeds, run as a subprocess from `cwd`."""
    r = subprocess.run([sys.executable, f"{REPO}/runs/RBT-71/measure.py", "804", "805", "806"],
                       cwd=cwd, capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": REPO})
    if r.returncode != 0:
        return None, r.stderr.strip().splitlines()[-3:]
    return r.stdout, []


def tamper_check():
    """Perturb ONE cell of one committed input and confirm the readout moves.

    Byte-identical output is only evidence of reproduction if the output is *derived* from
    the committed inputs. A measure.py that ignored them and printed a canned readout would
    also be byte-identical. This is the check that tells the two apart: season 599's holistic
    mean lifetime score in forage-804 feeds the `gain hol/wheel at 599` scorecard cell and
    R1's mean lead, and nothing else, so a correct derivation moves exactly those.
    """
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(f"{REPO}/{ROOT}", f"{tmp}/{ROOT}")
        p = f"{tmp}/{ROOT}/forage-804/seasons.txt"
        lines = open(p).read().splitlines()
        for i, line in enumerate(lines):
            f = line.split("\t")
            if f[0] == "599" and f[1] == "holistic":
                was = f[5]
                f[5] = "9.0"
                lines[i] = "\t".join(f)
                break
        else:
            print("   -> could not find the cell to perturb; check SKIPPED")
            return None
        open(p, "w").write("\n".join(lines) + "\n")
        out, err = run_measure(tmp)
    if out is None:
        print(f"   -> measure.py failed on the perturbed tree: {err}")
        return False
    ref = open(f"{ROOT}/readout-all.txt").read()
    moved, _ = line_delta(out, ref)
    print(f"   forage-804 season 599 holistic mean lifetime score {was} -> 9.0")
    print(f"   -> {moved} readout lines moved" + (
        "; the readout is DERIVED from the committed inputs, not replayed"
        if moved else "; NOTHING MOVED -- the readout does not depend on its inputs"))
    return moved > 0


def reproducibility():
    print("1. REPRODUCIBILITY -- can the scorecard be re-derived from the repository alone?")
    for seed in SEEDS:
        for kind in ("forage", "neutral"):
            run = f"{ROOT}/{kind}-{seed}"
            have = sorted(os.listdir(run)) if os.path.isdir(run) else []
            print(f"   {run:28} committed: {have or '(absent)'}")
    bulk = [f"{ROOT}/{k}-{s}/{n}" for s in SEEDS for k in ("forage", "neutral") for n in BULK
            if os.path.exists(f"{ROOT}/{k}-{s}/{n}")]
    print(f"   bulk present in this tree: {len(bulk)} of {len(SEEDS) * 2 * len(BULK)} "
          f"({'a fresh checkout -- the case this check is about' if not bulk else 'NOT a fresh checkout'})")

    print("\n   running: python runs/RBT-71/measure.py 804 805 806")
    out, err = run_measure(REPO)
    if out is None:
        print(f"   -> measure.py FAILED: {err}")
        return False
    ref = open(f"{ROOT}/readout-all.txt").read()
    if out == ref:
        print("   -> byte-identical to runs/RBT-71/readout-all.txt")
    else:
        n, where = line_delta(out, ref)
        print(f"   -> DIFFERS from readout-all.txt on {n} lines: {'; '.join(where)}")
        return False

    print("\n   tamper check -- is that agreement a derivation or a replay?")
    derived = tamper_check()
    print(f"   -> REPRODUCIBLE FROM THE REPOSITORY: {'yes' if derived else 'NOT ESTABLISHED'}")
    return bool(derived)


def consistency():
    print("\n2. INTERNAL CONSISTENCY -- REPORT.md scorecard against the committed readouts")
    report = open(f"{ROOT}/REPORT.md").read()
    ok = True
    for seed in SEEDS:
        ro = open(f"{ROOT}/readout-{seed}.txt").read()
        get = lambda p: (re.search(p, ro).group(1) if re.search(p, ro) else "??")
        vals = {
            "R1 fraction": get(r"holistic leads in ([\d.]+) of seasons"),
            "R2 holistic": get(r"\[selected\] heritability hol \+?(-?[\d.]+)"),
            "founders sel": get(r"\[selected\] founders  hol (\d+) of 60"),
            "founders neu": get(r"\[neutral\] founders  hol (\d+) of 60"),
        }
        for k, v in vals.items():
            here = v in report
            ok &= here
            print(f"   {seed} {k:14} {v:>8}   {'in REPORT.md' if here else 'NOT IN REPORT'}")
    print(f"   -> scorecard {'matches its readouts exactly' if ok else 'DISAGREES with its readouts'}")
    return ok


def what_r2_certifies():
    print("\n3. WHAT R2 CERTIFIES -- does a drift population clear the same bar?")
    print(f"   {'seed':<6} {'selected hol':>13} {'neutral hol':>12} {'neutral WHEEL':>14}  clears R2 (>=0.20)?")
    drift_clears = 0
    for seed in SEEDS:
        ro = open(f"{ROOT}/readout-{seed}.txt").read()
        sel = float(re.search(r"\[selected\] heritability hol \+?(-?[\d.]+)", ro).group(1))
        neu = float(re.search(r"\[neutral\] heritability hol \+?(-?[\d.]+)", ro).group(1))
        nw = float(re.search(r"\[neutral\] heritability hol [^ ]+ \(n=\d+\)\s+wheel \+?(-?[\d.]+)", ro).group(1))
        hit = nw >= 0.20
        drift_clears += hit
        print(f"   {seed:<6} {sel:>13.3f} {neu:>12.3f} {nw:>14.3f}  "
              f"{'YES -- drift passes R2' if hit else 'no'}")
    print(f"   -> the neutral WHEELED control clears R2 on {drift_clears} of {len(SEEDS)} seeds, "
          f"with no selection acting at all.")
    print("      R2 therefore certifies 'lifetime yield is a heritable measurement' (which is what")
    print("      the report says it tests) and NOT 'selection produced the heritability'.")
    return drift_clears


if __name__ == "__main__":
    reproducibility()
    consistency()
    what_r2_certifies()
