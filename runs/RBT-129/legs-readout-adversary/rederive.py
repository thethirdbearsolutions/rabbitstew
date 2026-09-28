"""RBT-129 legs-readout adversary: re-derive all 18 designed PAYS rows from the 36 ckpt/rbt-129-stage0-pays-* outputs,
with this file's own parsers and hard-coded t quantiles (numpy only), independently of legs_readout.py.

Per cell:
  prize   RBT-106's at a = 6: per population the mean over signed bodies of the per-body delta (the harness's income
          table), all 10 populations (a missing ROW counts 0), t(9) 95%; LB > 0.  Leave-one-population-out t(8) LBs.
  steps   the registered A1.4 line from the per-host table: nose (w3.4 - w3) minus per-unit speed
          ((speed@w3 - w3) x 0.25 / (r@w3 - 1), hosts with r@w3 >= 1.10), t(n-1) 95% / 90%, reading in steps.py's
          order; checked against the printed STEP row (the reading used is the STEP row's; the table is 3-decimal).
          Also the raw line's reading (the STEP row), the nose step and the per-unit speed step alone, and
          leave-one-host-out readings.
  r       per host r@w3; hosts with r outside [0.5, 2.0] are listed ("implausible for a damping / 1.25 step");
          the nose step of excluded (r < 1.10) against included hosts (is the exclusion correlated with the outcome?).
  warn    MuJoCo QACC / EPA warning counts in the cell's .err files.

    python rederive.py PAYS_DIR     (PAYS_DIR/<cell>-{prize,steps}/..., extracted from the branches' run.tar.gz)
"""
import glob, os, re, sys
import numpy as np

T975 = {1: 12.706205, 2: 4.302653, 3: 3.182446, 4: 2.776445, 5: 2.570582, 6: 2.446912, 7: 2.364624, 8: 2.306004,
        9: 2.262157, 10: 2.228139, 11: 2.200985, 12: 2.178813, 13: 2.160369, 14: 2.144787}
T95 = {1: 6.313752, 2: 2.919986, 3: 2.353363, 4: 2.131847, 5: 2.015048, 6: 1.943180, 7: 1.894579, 8: 1.859548,
       9: 1.833113, 10: 1.812461, 11: 1.795885, 12: 1.782288, 13: 1.770933, 14: 1.761310}
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
P = sys.argv[1] if __name__ == "__main__" else None


def ci(x, tab=T975):
    x = np.asarray(x, float); n = len(x)
    if n < 2:
        return (float(x.mean()) if n else float("nan")), float("nan"), float("nan")
    h = tab[n - 1] * x.std(ddof=1) / np.sqrt(n)
    return x.mean(), x.mean() - h, x.mean() + h


def reading(d):
    m, lo, hi = ci(d); _, l9, h9 = ci(d, T95)
    return "NOSE LEADS" if lo > 0 else "SPEED LEADS" if hi < 0 else "COMPARABLE" if (-0.1 < l9 and h9 < 0.1) else "TIED"


def prize_pop(path):
    if not os.path.exists(path):
        return None, None
    txt = open(path).read()
    if not re.search(r"^ROW ", txt, re.M):
        return None, None
    sec, d = None, []
    for ln in txt.splitlines():
        if ln.startswith("## "):
            sec = ln
        elif sec and sec.startswith("## Income") and re.match(r"^g\d+\s", ln):
            f = ln.replace("|", " ").split()
            d.append(float(f[3]))
    mot = re.search(r"^\s+motif\s+([+-][\d.]+)", txt, re.M)
    dec = re.search(r"^\s+rotated decoy\s+([+-][\d.]+)", txt, re.M)
    return float(np.mean(d)), (float(mot.group(1)) - float(dec.group(1))) if dec else None


def steps_table(path):
    head, rows, step = None, {}, {}
    for ln in open(path):
        if ln.startswith("| host |"):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
        elif head and ln.startswith("| O1/"):
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            rows[c[0]] = {k: float(v) for k, v in zip(head[1:], c[1:])}
        elif ln.startswith("STEP") and "w 3 -> 3.4" in ln:
            m = re.search(r"vs raw speed@w3: ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)] (.+?) \| vs per-unit speed \(n (\d+)\): ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\] (.+)$", ln.strip())
            step = dict(raw=m.group(4).strip(), raw_ci=tuple(float(m.group(i)) for i in (1, 2, 3)), n=int(m.group(5)),
                        pu_ci=tuple(float(m.group(i)) for i in (6, 7, 8)), pu=m.group(9).strip())
    return rows, step



def main():
    cells = sorted({os.path.basename(d).rsplit("-", 1)[0] for d in glob.glob(os.path.join(P, "*-prize"))},
                   key=lambda c: (c.split("-")[2], c.split("-")[3], c.split("-")[0]))
    print("| cell | prize t(9) | LB>0 | prize LOO LB min | STEP per-unit (n) | reading | my recompute (n) | my reading | raw reading | nose w3->3.4 | per-unit speed | PAYS | steps LOO readings | r@w3 outside [0.5,2] (host: r) | nose step: excluded vs included | QACC/EPA |")
    print("|---|" * 16 + "|")
    for cell in cells:
        pz = [prize_pop(os.path.join(P, f"{cell}-prize", "prize", f"{s}.txt")) for s in SEEDS]
        pr = [p[0] if p[0] is not None else 0.0 for p in pz]
        m, lo, hi = ci(pr)
        loo_p = min(ci([pr[j] for j in range(10) if j != i])[1] for i in range(10))
        rows, st = steps_table(os.path.join(P, f"{cell}-steps", "steps", "designed.txt"))
        inc = {h: v for h, v in rows.items() if v["r@w3"] >= 1.10}
        # a printed 1.100 may be < 1.10 in full precision: match the tool's n by dropping printed-1.100 hosts first if needed
        if len(inc) != st["n"]:
            inc = {h: v for h, v in rows.items() if v["r@w3"] > 1.10}
        nose = {h: v["w3.4"] - v["w3"] for h, v in rows.items()}
        unit = {h: (v["speed@w3"] - v["w3"]) * 0.25 / (v["r@w3"] - 1.0) for h, v in inc.items()}
        d = [nose[h] - unit[h] for h in inc]
        mm, ml, mh = ci(d)
        myr = reading(d)
        loo = sorted({reading([nose[h] - unit[h] for h in inc if h != k]) for k in inc})
        pays = lo > 0 and st["pu"].startswith(("NOSE LEADS", "COMPARABLE"))
        odd = [(h.split("final/")[0].split("/")[1] + "/" + h.split("/")[-1][:3], round(v["r@w3"], 2)) for h, v in rows.items() if not 0.5 <= v["r@w3"] <= 2.0]
        exc = [nose[h] for h in rows if h not in inc]
        warn = [open(f).read() for f in glob.glob(os.path.join(P, f"{cell}-*", "*", "*.err"))]
        q = sum(w.count("QACC") for w in warn); e = sum(w.count("EPA") for w in warn)
        print(f"| {cell} | {m:+.3f} [{lo:+.3f}, {hi:+.3f}] | {'yes' if lo > 0 else 'no'} | {loo_p:+.3f} | {st['pu_ci'][0]:+.3f} [{st['pu_ci'][1]:+.3f}, {st['pu_ci'][2]:+.3f}] ({st['n']}) | {st['pu']} | "
              f"{mm:+.3f} [{ml:+.3f}, {mh:+.3f}] ({len(d)}) | {myr} | {st['raw']} | {ci(list(nose.values()))[0]:+.3f} [{ci(list(nose.values()))[1]:+.3f}] | "
              f"{ci(list(unit.values()))[0]:+.3f} [{ci(list(unit.values()))[1]:+.3f}, {ci(list(unit.values()))[2]:+.3f}] | {'**PAYS**' if pays else 'no'} | {'/'.join(loo)} | "
              f"{odd if odd else '-'} | {np.mean(exc) if exc else float('nan'):+.3f} (n {len(exc)}) vs {np.mean([nose[h] for h in inc]):+.3f} (n {len(inc)}) | {q}/{e} |")


if __name__ == "__main__":
    main()
