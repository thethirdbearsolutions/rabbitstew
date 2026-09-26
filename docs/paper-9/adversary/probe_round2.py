"""Paper 9 adversary, round 2 (RBT-109): C4 probes on the paper at 9ec52bf.

Reads committed text only. Run from the root of a checkout of results/RBT-109-paper9:

    python <this file> > probe_round2.txt
"""
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
PAPER = (ROOT / "docs/paper-9-net-of-arithmetic.md").read_text()
REPORT = (ROOT / "runs/RBT-101/REPORT.md").read_text()


def main():
    p = print
    p("Paper 9 adversary, round 2: C4 probes")
    p("")
    p("G  C4: EVERY PREDICTOR THE MERGED REPORT PRINTS, AND ITS RESIDUAL (runs/RBT-101/REPORT.md §4 table)")
    sec = REPORT[REPORT.index("**Predictors of the paired recovery contrast"):REPORT.index("**Per fauna, Z10")]
    for ln in sec.splitlines():
        if ln.startswith("| ") and not ln.startswith("| predictor") and "---" not in ln:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            p(f"   {cells[1][:40]:<40} predicted {cells[2]:<22} residual {cells[3]:<34} [{cells[0][:48]}]")
    p("   => the residual's sign depends on the predictor: the registered prior as registered (half-discount)")
    p("      leaves -0.296, resolved TOWARD THE DESIGNED BODY; the post hoc arena predictors leave +0.17 (resolved),")
    p("      +0.24 (unresolved); the same-season split +0.27 (resolved).")
    p("")
    p("   Where the paper prints the registered half-discount residual -0.296:")
    hits = [i + 1 for i, ln in enumerate(PAPER.splitlines()) if "0.296" in ln]
    p(f"   lines {hits if hits else 'none'}")
    p("   Where the paper prints the Z residual +0.243:")
    hits = [i + 1 for i, ln in enumerate(PAPER.splitlines()) if "0.243" in ln]
    p(f"   lines {hits if hits else 'none'}")
    p("")
    p("H  'FIRST' / 'ONLY' RESOLVED NON-ARITHMETIC EFFECT, in the paper's own voice")
    for i, ln in enumerate(PAPER.splitlines(), 1):
        if re.search(r"\b(first|only) (resolved|sign)", ln):
            p(f"   l.{i}: {ln.strip()[:150]}")
    p("   against the paper's own §4 table: C2's alive-end residual -0.318 [-0.498, -0.138] is merged (RBT-99, 19:10),")
    p("   resolved, and predates C4; the paper's S11c -0.260 [-0.448, -0.071] resolves too.")


if __name__ == "__main__":
    sys.exit(main())
