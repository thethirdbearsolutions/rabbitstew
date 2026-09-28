"""RBT-129 Stage P + Stage 0 readout, per READOUT-PLAN.md (committed before any output was opened).

    python3 runs/RBT-129/stageP0-readout/stageP0_readout.py DATA [--replace UNIT=DIR ...] > stageP0_readout.txt

DATA holds the restored run directories at their launch paths (DATA/runs/RBT-129/stage{P,0}/...), each restored
with scripts/durable.sh from its ckpt/rbt-129-* branch; the four -unit branches at stageP/<point>/129001/unitbr.
--replace points a DUP-VERIFY unit (e.g. P/c1-p030-U-L/129002/S) at its clean re-run's directory.
Writes pilot_constants.json beside this file.
"""
import glob, importlib.util, json, math, os, re, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-129", "launch"))
import stages  # noqa: E402  (k1_compare, K1_SKIP)
_spec = importlib.util.spec_from_file_location("regime", os.path.join(ROOT, "scripts", "regime.py"))
rg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(rg)

PILOT = ("c1-p030-U-L", "c0-p030-U-L", "c1-p030-PW-G", "c2-p030-PW-G")
SEEDS_P = (129001, 129002, 129003, 129004)
SEEDS_0 = (129001, 129002, 129003)
H, D, NB = "holistic", "conventional", "null_b"
WIN = (240, 299)


def price(d):
    return json.load(open(os.path.join(d, "config.json")))["sim"]["food"]["work_cost"]


def cost(d):
    return float(json.load(open(os.path.join(d, "config.json")))["ecology"]["living_cost"])


def rows(d):
    with open(os.path.join(d, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r.get("death") in ("cull", "merge-null"):
                continue
            yield r


_xcheck = {"n": 0, "bad": 0}


def net(r, p):
    v = r.get("food", 0.0) - p * r.get("work", 0.0) / 1000.0
    _xcheck["n"] += 1
    if abs(v - r.get("last_score", v)) > 2e-3:
        _xcheck["bad"] += 1
    return v


def flows(d, lo, hi, kinds=(H, D)):
    """{kind: (mean season net over member-seasons in [lo, hi], count)}"""
    p = price(d)
    acc = {k: [0.0, 0] for k in kinds}
    for r in rows(d):
        if lo <= r["generation"] <= hi and r["population"] in acc:
            a = acc[r["population"]]; a[0] += net(r, p); a[1] += 1
    return {k: ((s / n) if n else None, n) for k, (s, n) in acc.items()}


def history(d):
    h = json.load(open(os.path.join(d, "history.json")))["history"]
    out = {}
    for e in h:
        out[(e["season"], e["population"])] = e
    return out


def sd(xs):
    return st.stdev(xs) if len(xs) >= 2 else None


def f(x, fmt="{:+.3f}"):
    return "--" if x is None else fmt.format(x)


# ------------------------------------------------------------------------------------------------ integrity

def integrity(data):
    P = os.path.join(data, "runs", "RBT-129")
    out = []
    lanes = sorted(glob.glob(os.path.join(ROOT, "runs/RBT-129/lanes/P-0/*.jsonl")))
    jobs = [(os.path.basename(p), json.loads(l)) for p in lanes for l in open(p) if l.strip()]
    missing_dir, missing_mark, skipped = [], [], []
    for lane, j in jobs:
        d = os.path.join(data, j["dir"])
        tag = j["name"].split("/")[-1]
        if not os.path.isdir(d):
            missing_dir.append(j["name"]); continue
        m = os.path.join(d, f".rbt129-done-{tag}")
        if not os.path.exists(m):
            missing_mark.append(j["name"])
        elif "skipped" in open(m).read():
            skipped.append((j["name"], open(m).read().strip()))
    out.append(f"jobs in the 20 P-0 lane files: {len(jobs)}")
    out.append(f"run directories restored: {len(jobs) - len(missing_dir)} of {len(jobs)}; missing: {missing_dir or 'none'}")
    out.append(f"done-markers present: {len(jobs) - len(missing_dir) - len(missing_mark)}; missing: {missing_mark or 'none'}")
    out.append(f"jobs skipped by the lane fix (marker note): {len(skipped)}")
    for n, note in skipped:
        out.append(f"  {n}: {note.split(' ', 1)[1] if ' ' in note else note}")
    # extinct pre-merge units and all-empty ckpt60s
    out.append("pilot units: EXTINCT.txt (record) and ckpt60 state")
    extinct = {}
    for pt in PILOT:
        for s in SEEDS_P:
            u = os.path.join(P, "stageP", pt, str(s))
            e = None
            for c in (os.path.join(u, "record", "EXTINCT.txt"), os.path.join(u, "EXTINCT.txt")):
                if os.path.exists(c):
                    e = open(c).readline().strip()
            ck = os.path.join(u, "ckpt60", "state.json")
            ckd, empty = None, False
            if os.path.exists(ck):
                stt = json.load(open(ck))
                empty = all(len(v) == 0 for v in stt["populations"].values())
                ckd = f"season {stt['season']}, " + ", ".join(f"{k} {len(v)}" for k, v in sorted(stt["populations"].items()))
            if e:
                extinct[(pt, s)] = e
            if e or empty:
                out.append(f"  {pt}/{s}: {e or 'no EXTINCT.txt'} | ckpt60: {ckd or 'absent'}")
    out.append(f"  extinct pre-merge units: {len(extinct)} ({', '.join(f'{a}/{b}' for a, b in extinct)})")
    # K1, in check_branches' registered order
    out.append("K1 per point (source order: record K1.txt, K1fork marker, -unit branch, recompute)")
    for pt in PILOT:
        u = os.path.join(P, "stageP", pt, "129001")
        verdict, src = None, None
        for path, label in ((os.path.join(u, "record", "K1.txt"), "record"),
                            (os.path.join(u, "K1fork", ".rbt129-done-K1"), "K1fork marker"),
                            (os.path.join(u, "unitbr", "K1.txt"), "-unit branch")):
            if os.path.exists(path):
                t = open(path).read()
                mm = re.search(r"K1 (PASS|FAIL|UNTESTABLE[^\n:]*)", t)
                if mm:
                    verdict, src = mm.group(1), label; break
        if verdict is None and os.path.isdir(os.path.join(u, "K1ref")) and os.path.isdir(os.path.join(u, "K1fork")):
            verdict, src = stages.k1_compare(os.path.join(u, "K1ref"), os.path.join(u, "K1fork"))[0], "recomputed"
        ub = glob.glob(os.path.join(u, "unitbr", "*"))
        out.append(f"  {pt}: K1 {verdict} ({src}); -unit branch files: {sorted(os.path.basename(x) for x in ub) or 'none'}")
        if verdict and verdict.startswith("UNTESTABLE"):
            alt = [s for s in SEEDS_P if (pt, s) not in extinct]
            alts = [s for s in alt if os.path.isdir(os.path.join(P, "stageP", pt, str(s), "K1ref"))]
            out.append(f"    lowest seed reaching season 60: {alt[0] if alt else 'none'}; a K1 re-run on it in the data: "
                       f"{alts or 'none (no K1ref/K1fork branch for it)'}")
    # the free K1-type control: pilot ckpt60 vs census S at the 4 points x 129001-129003
    out.append("free K1-type control (DESIGN 11.1 note): pilot ckpt60 vs census 0/<point>/<seed>/S, k1_compare")
    for pt in PILOT:
        for s in SEEDS_0:
            a = os.path.join(P, "stage0", pt, str(s), "S")
            b = os.path.join(P, "stageP", pt, str(s), "ckpt60")
            if (pt, s) in extinct or not os.path.exists(os.path.join(b, "state.json")):
                bb = os.path.join(P, "stageP", pt, str(s), "S")  # extinct units: S stopped at extinction, never resumed
                v, lines = stages.k1_compare(a, bb) if os.path.isdir(bb) else ("ABSENT", [])
                out.append(f"  {pt}/{s}: {v} (extinct pre-merge: S against census S) {'; '.join(lines[:4])}")
            else:
                v, lines = stages.k1_compare(a, b)
                out.append(f"  {pt}/{s}: {v} {'; '.join(lines[:4])}")
    return out, extinct


# ------------------------------------------------------------------------------------------------ pilot

def arm_dir(data, pt, s, arm, repl):
    key = f"P/{pt}/{s}/{arm}"
    return repl.get(key, os.path.join(data, "runs", "RBT-129", "stageP", pt, str(s), arm))


def yprime(d, K):
    """(y', both alive at the merge, nK59, nOther59): share of the K label over 240-299 minus nK/(nK+nOther) at 59."""
    h = history(d)
    other = D if K == H else H
    nK = h.get((59, K), {}).get("alive", 0)
    nO = h.get((59, other), {}).get("alive", 0)
    s0 = nK / max(1, nK + nO)
    sh = [h.get((s, K), {}).get("alive", 0) / 120.0 for s in range(WIN[0], WIN[1] + 1)]
    return st.mean(sh) - s0, (nK > 0 and nO > 0), nK, nO


def season_costs(d, lo=60, hi=299):
    """mean core-s per season over [lo, hi] from run.log, x2 (WORKERS = 2), and the number of --resume invocations."""
    ts = []
    for line in open(os.path.join(d, "run.log")):
        m = re.match(r"season\s+(\d+) .*\((\d+(?:\.\d+)?)s\)\s*$", line)
        if m and lo <= int(m.group(1)) <= hi:
            ts.append(float(m.group(2)))
    resumes = sum(1 for l in open(os.path.join(d, "command.txt")) if "--resume" in l)
    return (2 * st.mean(ts) if ts else None), len(ts), resumes


def pilot(data, extinct, repl):
    out = ["## Pilot constants (plan section 3)", ""]
    sds, ns, per_point = {}, {}, {}
    out.append("(a) per-seed H - D income flow, S arm, seasons 240-299 (food - p * work/1000, living rows)")
    for pt in PILOT:
        xs = []
        for s in SEEDS_P:
            if (pt, s) in extinct:
                out.append(f"  {pt}/{s}: extinct pre-merge, excluded"); continue
            fl = flows(arm_dir(data, pt, s, "S", repl), *WIN)
            if fl[H][0] is None or fl[D][0] is None:
                out.append(f"  {pt}/{s}: H {f(fl[H][0])} (n {fl[H][1]}), D {f(fl[D][0])} (n {fl[D][1]}): a fauna has no rows in 240-299, excluded")
                continue
            xs.append(fl[H][0] - fl[D][0])
            out.append(f"  {pt}/{s}: H {fl[H][0]:+.3f} (n {fl[H][1]}), D {fl[D][0]:+.3f} (n {fl[D][1]}), H - D {xs[-1]:+.3f}")
        per_point[pt] = xs
        out.append(f"  {pt}: n {len(xs)}, mean H - D {f(st.mean(xs) if xs else None)} (descriptive), per-seed SD {f(sd(xs), '{:.3f}')}")
    ok = {pt: xs for pt, xs in per_point.items() if len(xs) >= 3}
    sd_min = min(sd(x) for x in ok.values()) if ok else None
    sd_max = max(sd(x) for x in ok.values()) if ok else None
    dfp = sum(len(x) - 1 for x in ok.values())
    pooled = math.sqrt(sum((len(x) - 1) * sd(x) ** 2 for x in ok.values()) / dfp) if dfp else None
    two = {pt: xs for pt, xs in per_point.items() if len(xs) >= 2}
    df2 = sum(len(x) - 1 for x in two.values())
    sd_desc = math.sqrt(sum((len(x) - 1) * sd(x) ** 2 for x in two.values()) / df2) if df2 else None
    out.append(f"  descriptive only (not a registered constant): pooled SD over points with n >= 2 {sorted(two)}: {f(sd_desc, '{:.3f}')} (df {df2})")
    out.append(f"  points with n >= 3: {sorted(ok)}; SD min {f(sd_min, '{:.3f}')}, max {f(sd_max, '{:.3f}')}, pooled {f(pooled, '{:.3f}')} (df {dfp})")
    out.append("")
    out.append("(b) null y' per N arm (K = kept fauna; y' = share(K) 240-299 - nK/(nK+nOther) at 59)")
    ys, yk = [], {H: [], D: []}
    for pt in PILOT:
        for s in SEEDS_P:
            if (pt, s) in extinct:
                continue
            d = arm_dir(data, pt, s, "N", repl)
            K = H if s % 2 else D
            y, both, nK, nO = yprime(d, K)
            tag = "" if both else "  EXCLUDED: a fauna extinct at the merge (DESIGN 6.1 item 2: not valid for the share test)"
            out.append(f"  {pt}/{s} N (K {K}): nK {nK} nOther {nO} y' {y:+.3f}{tag}")
            if both:
                ys.append(y); yk[K].append(y)
    null_sd = sd(ys)
    dfk = sum(len(v) - 1 for v in yk.values() if v)
    pooled_k = math.sqrt(sum(sum((y - st.mean(v)) ** 2 for y in v) for v in yk.values() if v) / dfk) if dfk > 0 else None
    out.append(f"  null y' SD (registered constant): {f(null_sd, '{:.3f}')} over {len(ys)} runs (df {len(ys) - 1})")
    out.append(f"  kind-offset-removed pooled SD (descriptive): {f(pooled_k, '{:.3f}')} (df {dfk}; H n {len(yk[H])}, D n {len(yk[D])})")
    out.append("  M arms' y' (K = holistic), descriptive:")
    for pt in PILOT:
        for s in SEEDS_P:
            if (pt, s) in extinct:
                continue
            y, both, nK, nO = yprime(arm_dir(data, pt, s, "M", repl), H)
            out.append(f"    {pt}/{s} M: nH {nK} nD {nO} y' {y:+.3f}{'' if both else ' (a fauna extinct at the merge)'}")
    out.append("")
    rep = []
    for line in open(os.path.join(ROOT, "runs/RBT-129/power.txt")):
        m = re.match(r"\s*lottery\s+g0 (\S+) edge \+0\.00 tau 0\.0: y' \S+ sd (\S+)", line)
        if m:
            rep.append(float(m.group(2)))
    rep_sd = st.mean(rep)
    r = null_sd / rep_sd if null_sd else None
    out.append(f"(c) replica null y' SD (power.txt section 2, lottery, edge 0, tau 0; {len(rep)} rows {rep}): {rep_sd:.4f};"
               f" r = real/replica = {f(r, '{:.3f}')}")
    out.append("")
    out.append("(d) cost per arm-season (run.log per-season wall s x 2 cores; seasons 60-299)")
    costs, by_pt, excl = [], {}, []
    for pt in PILOT:
        for s in SEEDS_P:
            if (pt, s) in extinct:
                continue
            for arm in ("S", "M", "N"):
                if f"P/{pt}/{s}/{arm}" in repl:
                    excl.append(f"{pt}/{s}/{arm} (DUP-VERIFY re-run: timed on the readout container, not a launch host)")
                    continue
                c, n, res = season_costs(arm_dir(data, pt, s, arm, repl))
                if c is None or res > 1:
                    excl.append(f"{pt}/{s}/{arm} ({'no season lines' if c is None else f'{res} --resume invocations'})")
                    continue
                costs.append(c); by_pt.setdefault(pt, []).append(c)
    med = st.median(costs)
    ptmax = max(st.mean(v) for v in by_pt.values())
    for pt, v in by_pt.items():
        out.append(f"  {pt}: {len(v)} arms, mean {st.mean(v):.1f} core-s, range {min(v):.1f}-{max(v):.1f}")
    out.append(f"  excluded: {excl or 'none'}")
    out.append(f"  median over {len(costs)} arms {med:.1f} core-s (replaces 20); max per-point mean {ptmax:.1f} (replaces 25)")
    out.append(f"  last_score cross-check: {_xcheck['bad']} of {_xcheck['n']} rows differ from food - p*work/1000 by > 0.002")
    rd = lambda x, k=4: None if x is None else round(x, k)
    const = {"sd_bounds": [rd(sd_min), rd(sd_max)], "sd_pooled": rd(pooled), "sd_pooled_df": dfp,
             "null_sd": rd(null_sd), "null_runs": len(ys), "replica_null_sd": rd(rep_sd),
             "y_scale": rd(r), "core_s": [rd(med, 2), rd(ptmax, 2)], "sd_descriptive": rd(sd_desc)}
    json.dump(const, open(os.path.join(HERE, "pilot_constants.json"), "w"), indent=2)
    out.append(f"  pilot_constants.json: {json.dumps(const)}")
    return out


# ------------------------------------------------------------------------------------------------ census

def census_points(data):
    return sorted(os.listdir(os.path.join(data, "runs", "RBT-129", "stage0")))


def census(data):
    out = ["## Stage 0 census layer (plan section 6)", ""]
    C = os.path.join(data, "runs", "RBT-129", "stage0")
    res = {}
    for pt in census_points(data):
        R = {"ext": {H: 0, D: 0}, "solv": {H: [0, 0], D: [0, 0]}, "sat": {H: [], D: []}, "via": {H: [], D: []},
             "g0": [0.0, 0], "flow": {H: [0.0, 0], D: [0.0, 0]}, "births": {H: 0, D: 0}, "starv": {H: [], D: []}}
        for s in SEEDS_0:
            d = os.path.join(C, pt, str(s), "S")
            h = history(d)
            lc, p = cost(d), price(d)
            for k in (H, D):
                e = h.get((59, k))
                if e is None or e["alive"] - e["births"] == 0:
                    R["ext"][k] += 1
                R["births"][k] += sum(v["births"] for (ss, kk), v in h.items() if kk == k)
            fs = {}
            for r in rows(d):
                g, k = r["generation"], r["population"]
                v = net(r, p)
                if not r["parents"] and g <= 11:
                    fs.setdefault((k, r["name"]), []).append(v)
                if 30 <= g <= 59:
                    R["g0"][0] += v; R["g0"][1] += 1
                    R["flow"][k][0] += v; R["flow"][k][1] += 1
            for (k, _), vs in fs.items():
                R["solv"][k][0] += st.mean(vs) >= lc; R["solv"][k][1] += 1
            reg = rg.regime(d, windows=((30, 59),))
            for k in (H, D):
                w = (reg["fauna"].get(k) or [{}])[0]
                if w.get("saturation_local") is not None:
                    R["sat"][k].append(w["saturation_local"])
                if w.get("viability") is not None:
                    R["via"][k].append(w["viability"])
                if (w.get("death_share") or {}).get("starvation") is not None:
                    R["starv"][k].append(w["death_share"]["starvation"])
        res[pt] = R
    ff = {k: [pt for pt, R in res.items() if R["ext"][k] >= 2] for k in (H, D)}
    out.append("C2 FOUNDING-FAIL (extinct at 59 before refill on >= 2 of 3 seeds; provisional, flagged; never EXCLUDED):")
    for k in (H, D):
        out.append(f"  {k}: {len(ff[k])} of {len(res)} points: {', '.join(ff[k]) or 'none'}")
    out.append("  seeds extinct per fauna (points with any): " + "; ".join(
        f"{pt} H{R['ext'][H]} D{R['ext'][D]}" for pt, R in res.items() if R["ext"][H] or R["ext"][D]))
    out.append("")
    out.append("per point (seeds pooled): extinct seeds H/D | founder solvency H/D | saturation_local 30-59 H/D (mean of seeds) |"
               " viability H/D | starvation share of deaths H/D | census g0 | flow H, D, H - D (30-59) | births H/D")
    diff = {}
    for pt, R in res.items():
        fl = {k: (R["flow"][k][0] / R["flow"][k][1] if R["flow"][k][1] else None) for k in (H, D)}
        diff[pt] = fl[H] - fl[D] if None not in fl.values() else None
        g0 = R["g0"][0] / R["g0"][1] + 0.35 if R["g0"][1] else None
        R["g0v"], R["fl"] = g0, fl
        sv = {k: (R["solv"][k][0] / R["solv"][k][1] if R["solv"][k][1] else None) for k in (H, D)}
        R["sv"] = sv
        m = lambda xs: st.mean(xs) if xs else None
        out.append(f"  {pt:14s} {R['ext'][H]}/{R['ext'][D]} | {f(sv[H], '{:.2f}')}/{f(sv[D], '{:.2f}')} |"
                   f" {f(m(R['sat'][H]), '{:.2f}')}/{f(m(R['sat'][D]), '{:.2f}')} | {f(m(R['via'][H]), '{:.2f}')}/{f(m(R['via'][D]), '{:.2f}')} |"
                   f" {f(m(R['starv'][H]), '{:.2f}')}/{f(m(R['starv'][D]), '{:.2f}')} | {f(g0, '{:.3f}')} |"
                   f" {f(fl[H])}, {f(fl[D])}, {f(diff[pt])} | {R['births'][H]}/{R['births'][D]}")
    out.append("")
    # C1: rows along price (fixed c, L, s) and clutter (fixed p, L, s)
    parse = lambda pt: re.match(r"c(\d+)-p(\d+)-(\w+)-(\w)$", pt).groups()
    rows_p, rows_c = {}, {}
    for pt in res:
        c, p, L, s = parse(pt)
        rows_p.setdefault((c, L, s), []).append((int(p), pt))
        rows_c.setdefault((p, L, s), []).append((int(c) if c != "05" and c != "15" else {"05": 5, "15": 15}[c], pt))
    def cval(c):
        return {"0": 0, "05": 0.5, "1": 1, "15": 1.5, "2": 2}[c]
    broken = []
    for label, rr, keyf in (("price", rows_p, lambda x: x[0]), ("clutter", rows_c, None)):
        for key, pts in sorted(rr.items()):
            if label == "clutter":
                pts = sorted(pts, key=lambda x: cval(parse(x[1])[0]))
            else:
                pts = sorted(pts)
            sg = [diff[pt] for _, pt in pts if diff[pt] is not None]
            signs = [1 if x > 0 else -1 for x in sg if x != 0]
            ch = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
            if ch > 1:
                broken.append(f"{label} row {key}: {ch} sign changes: " + " ".join(f"{pt} {f(diff[pt])}" for _, pt in pts))
    out.append(f"C1 monotonicity: {len(broken)} rows with > 1 sign change (enter R-A's pair list at Stage 2a)")
    out += ["  " + b for b in broken]
    out.append("")
    out.append("side effects (R10) against c1-p030-U-L: descriptive, in the per-point table above (row c1-p030-U-L is the reference)")
    out.append("C3 (rest on c = 2): not in the P-0 lanes: NOT RUN.  PAYS (18 cells): read by #467/#487, not here.")
    return out, res


def main():
    data = sys.argv[1]
    repl = {}
    for a in sys.argv[2:]:
        if "=" in a and not a.startswith("--"):
            k, v = a.split("=", 1); repl[k] = v
    lines, extinct = integrity(data)
    print("# RBT-129 Stage P + Stage 0 readout (stageP0_readout.py; plan: READOUT-PLAN.md)")
    print("# replacements (DUP-VERIFY): " + (", ".join(f"{k} -> clean re-run" for k in repl) or "none"))
    print()
    print("## Integrity")
    print("\n".join(lines))
    print()
    if "--integrity-only" in sys.argv:
        return
    print("\n".join(pilot(data, extinct, repl)))
    print()
    print("\n".join(census(data)[0]))


if __name__ == "__main__":
    main()
