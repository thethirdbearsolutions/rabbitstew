"""RBT-90 part 2 adversary, probe X: which committed input can move which verdict line?

Copies runs/RBT-90/forage-*/ to a scratch tree, perturbs ONE kind of input file on every seed, runs the
unmodified part2_readout.py on the copy (its PART2_ARMS override), and reports which output lines changed.

  descent->590   every descent.txt replaced by the aggregator's descent-590.txt (the champion's DAG):
                 the seam.  If no scored regularity reads descent.txt, only the DAG rows may move.
  descent-junk   every descent.txt's JSON line replaced by absurd numbers: the same question, harder.
  control-osc    oscillator.txt's "distinct" set to 5 on every seed: a positive control that the
                 perturbation machinery does reach a verdict line.

usage: seam_probe.py
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ARMS = HERE.parent
READOUT = ARMS / "part2_readout.py"
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def readout(arms):
    return subprocess.run([sys.executable, str(READOUT)], capture_output=True, text=True, check=True,
                          env={**os.environ, "PART2_ARMS": str(arms)}).stdout.splitlines()


def edit_last_json(path, fn):
    lines = path.read_text().splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("{"):
            lines[i] = json.dumps(fn(json.loads(lines[i].replace("NaN", "null"))))
            break
    path.write_text("\n".join(lines) + "\n")


def perturb(tree, kind):
    for s in SEEDS:
        a = tree / f"forage-{s}"
        if kind == "descent->590":
            shutil.copy(a / "descent-590.txt", a / "descent.txt")
        elif kind == "descent-junk":
            edit_last_json(a / "descent.txt", lambda j: {**j, "ancestors": 9999, "founders": 99, "crossover_steps": 999,
                                                          "genomes_missing": 77, "verdict": "JUNK"})
        elif kind == "control-osc":
            edit_last_json(a / "oscillator.txt", lambda j: {**j, "distinct": 5})


if __name__ == "__main__":
    base = readout(ARMS)
    committed = (ARMS / "part2-readout.txt").read_text().splitlines()
    print(f"unperturbed readout identical to the committed part2-readout.txt: {base == committed}")
    for kind in ("descent->590", "descent-junk", "control-osc"):
        with tempfile.TemporaryDirectory() as t:
            tree = pathlib.Path(t)
            for s in SEEDS:
                shutil.copytree(ARMS / f"forage-{s}", tree / f"forage-{s}")
            perturb(tree, kind)
            out = readout(tree)
        changed = [(i, a, b) for i, (a, b) in enumerate(zip(base, out)) if a != b]
        verdict_lines = [i for i, a, b in changed if "->" in a or re.search(r"(pooled|composite).*holds", a)]
        dag_rows = [i for i, a, b in changed if re.match(r"\s*\d+ \|", a)]
        print(f"\n{kind}: {len(changed)} lines changed; DAG-table rows {len(dag_rows)}; tally or verdict lines "
              f"{len(verdict_lines)}; other {len(changed) - len(dag_rows) - len(verdict_lines)}")
        for i, a, b in changed[:12]:
            if i not in dag_rows or kind == "descent->590":
                print(f"  - {a}\n  + {b}")
