"""Paper 9 adversary (RBT-109): probes of the paper's numbers against committed files.

Reads only committed text on this branch; reuses rederive.py's parsers and t quantiles.
Run from the repository root:

    python docs/paper-9/adversary/probe_paper.py > docs/paper-9/adversary/probe_paper.txt
"""
import hashlib
import importlib.util
import io
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("rederive", ROOT / "docs/paper-9/rederive.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
SEEDS = R.SEEDS


def fmt(xs):
    return R.fmt(xs)


def main():
    p = print
    p("Paper 9 adversary: probes on docs/paper-9-net-of-arithmetic.md")
    p("")

    # A. rederive round trip ------------------------------------------------------------------
    buf = io.StringIO()
    with redirect_stdout(buf):
        R.main()
    fresh = buf.getvalue()
    committed = (ROOT / "docs/paper-9/rederive.txt").read_text()
    p("A  REDERIVE ROUND TRIP")
    p(f"   rederive.py stdout sha256 {hashlib.sha256(fresh.encode()).hexdigest()[:16]}  "
      f"committed rederive.txt sha256 {hashlib.sha256(committed.encode()).hexdigest()[:16]}  "
      f"identical: {fresh == committed}")
    p("")

    # B. placebo onsets: one computation, three files -----------------------------------------
    p("B  PLACEBO ONSETS: are C1, C2 and C3's 23/25 three tests or one?")
    seqs = {}
    for tag, rel in [("C2", "runs/RBT-99/placebo.txt"), ("C3", "runs/RBT-100/placebo.txt")]:
        txt = (ROOT / rel).read_text()
        seqs[tag] = re.findall(r"(T[+\-]\d+):([A-F]\d?)", txt.split("class A fires")[0])
    adv92 = (ROOT / "runs/RBT-92/readout-adversary/probe_readout.txt").read_text()
    blk = adv92[adv92.index("placebo onsets"):].split("class A fires")[0]
    c1 = re.findall(r"->\s*([A-F]\d?)\s*$", blk, re.M)
    p(f"   C1 (RBT-92 adversary P3) calls: {''.join(c1)}  ({c1.count('A')}/{len(c1)} A)")
    for tag, s in seqs.items():
        p(f"   {tag} placebo.txt calls:              {''.join(c for _, c in s)}  "
          f"({sum(c == 'A' for _, c in s)}/{len(s)} A); misses at {[o for o, c in s if c != 'A']}")
    same = [c for _, c in seqs["C2"]] == [c for _, c in seqs["C3"]] == c1
    p(f"   identical sequence in all three: {same}. The base arm and T are shared (RBT-99 adversary F4:")
    p("   'RBT-92's result by construction'), so [S4], [S9], [S16] are one placebo test, printed three times.")
    p("")

    # C. rounding drift: paper text vs rederive vs merged REPORT ---------------------------------
    p("C  ROUNDING: the paper's printed interval ends against rederive.txt rows it tags")
    r92 = (ROOT / "runs/RBT-92/readout.txt").read_text()
    hol = R.per_seed(R.line_with(r92, "R-shift  holistic     recovery"))
    con = R.per_seed(R.line_with(r92, "R-shift  conventional recovery"))
    obs2 = R.per_seed(R.line_with((ROOT / "runs/RBT-99/placebo.txt").read_text(), "event - base, R-body"))
    obs3 = R.per_seed(R.line_with((ROOT / "runs/RBT-100/placebo.txt").read_text(), "event - base, R-body"))
    rows = [
        ("S1 co-evolved R-shift C1", hol, "−0.020 [−0.073, +0.034]", "§3.1 l.210", "readout.txt full precision"),
        ("S3 paired C1", [h - c for h, c in zip(hol, con)], "+0.032 [−0.041, +0.105]", "abstract/table/§3.1", "disclosed in table note"),
        ("S7 paired C2", obs2, "+0.371 [+0.162, +0.581]", "table, §3.2", "not disclosed"),
        ("S13 paired C3", obs3, "+0.138 [+0.006, +0.271]", "table, §3.3", "not disclosed"),
    ]
    for name, xs, paper, where, note in rows:
        m, lo, hi, sd, pos, n = R.stat(xs)
        p(f"   [{name}] rederive (3-dp per-seed) {m:+.3f} [{lo:+.3f}, {hi:+.3f}]; paper prints {paper} at {where}; {note}")
    # full-precision lines, where the committed files print them
    for rel, needle in [("runs/RBT-92/readout.txt", "R-shift  holistic     recovery"),
                        ("runs/RBT-99/placebo.txt", "event - base, R-body"),
                        ("runs/RBT-100/placebo.txt", "event - base, R-body")]:
        ln = R.line_with((ROOT / rel).read_text(), needle)
        mm = re.search(r"mean ([+\-][\d.]+)\s+95% t\(9\) \[([+\-][\d.]+), ([+\-][\d.]+)\]", ln)
        p(f"   {rel}: full precision {mm.group(1)} [{mm.group(2)}, {mm.group(3)}]")
    p("   => the paper's figures are the committed files' full-precision values, correctly; but they are tagged")
    p("      [S1], [S7], [S13], whose printed ends differ in the third place. Only S3's drift is footnoted.")
    p("")

    # D. C2 post hoc insolvent end, and what the paper leaves out --------------------------------
    p("D  C2 INSOLVENT END (paper's S11b), re-derived independently from the adversary's P2 table")
    adv99 = (ROOT / "runs/RBT-99/readout-adversary/probe_readout.txt").read_text()
    hdr = None
    tab = {}
    for ln in adv99[adv99.index("P2 ARITHMETIC"):adv99.index("all ten:")].splitlines():
        if "base con inc" in ln:
            hdr = ln
        f = ln.split()
        if f and f[0].isdigit():
            tab[int(f[0])] = f
    p(f"   header: {hdr.strip()}")
    p("   column 13 (index 12) is 'base con inc': rederive.py reads the right column.")
    price_h = [float(tab[s][1]) for s in SEEDS]
    price_c = [float(tab[s][2]) for s in SEEDS]
    base_c = [float(tab[s][12]) for s in SEEDS]
    alive = [c - h for h, c in zip(price_h, price_c)]
    ins = [b - h for b, h in zip(base_c, price_h)]
    p(f"   alive end (price_c − price_h, P2 prices)       {fmt(alive)}")
    p(f"   insolvent end (base_c − price_h)               {fmt(ins)}")
    p(f"   ends differ by (base_c − price_c) per seed      {fmt([b - c for b, c in zip(base_c, price_c)])}")
    p(f"   residual obs − insolvent end [S11c]              {fmt([o - a for o, a in zip(obs2, ins)])}")
    p(f"   residual obs − alive end [S8]                    {fmt([o - a for o, a in zip(obs2, alive)])}")
    p("   => against BOTH ends the residual resolves, toward the designed body. The paper's §3.2 says the")
    p("      arithmetic 'accounts for all of the effect, and more' but does not print S11c; 'and more' is a")
    p("      designed-favouring residual that now resolves at both ends of the post hoc bracket.")
    p("")

    # E. C3 event − null, printed in the merged report, missing from the paper ---------------------
    p("E  C3 EVENT − NULL (registered paired contrast), merged REPORT §2 / placebo.txt P4")
    ln = R.line_with((ROOT / "runs/RBT-100/placebo.txt").read_text(), "event - null, R-body")
    p("   " + ln.strip()[:190])
    p("   => unresolved, 7/10. The paper's C2 row prints its event − null (n = 7, resolved); the C3 row and")
    p("      abstract print only event − base. Lesson 2 names event − null as half of the event readout.")
    p("")

    # F. power table: 'halving the MDE costs about four times the seeds on every row' --------------
    p("F  POWER: n for MDE 0.05 over n for MDE 0.10, per row of §8's table")
    sd1 = R.stat([h - c for h, c in zip(hol, con)])[3]
    for rid, sd in [("P1", 0.091), ("P2", sd1), ("P3", R.stat([o - a for o, a in zip(obs2, alive)])[3]),
                    ("P4", 0.153), ("P5", 0.128)]:
        a, b = R.n_for(sd, 0.10), R.n_for(sd, 0.05)
        p(f"   [{rid}] sd {sd:.3f}: n@0.10 {a:>3}, n@0.05 {b:>3}, ratio {b / a:.2f}")
    p("   => 3.1 to 3.9, not 'about four times ... on every row' (small-n t quantiles shrink the ratio).")


if __name__ == "__main__":
    sys.exit(main())
