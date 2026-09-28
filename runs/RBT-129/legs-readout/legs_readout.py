"""RBT-129 designed PAYS legs readout (READOUT-PLAN.md, committed pre-data at c47403c).

Reads ONLY the 36 checkpoint branches origin/ckpt/rbt-129-stage0-pays-<cell>-{prize,steps} (each a durable.sh
snapshot: MANIFEST + run.tar.gz.partNNN), unpacked into a temporary directory, plus the legs' launch records and the
cells' config.json at the launch commit 29ab80b.  No Stage P or Stage 0 census branch is touched.

    python legs_readout.py integrity  > integrity.txt      # step 1 of the plan; nothing else is computed
    python legs_readout.py readout    > legs_readout.txt   # steps 2-5 (refuses unless integrity passes)

Fetch the branches first:  git fetch origin '+refs/heads/ckpt/rbt-129-stage0-pays-*:refs/remotes/origin/ckpt/rbt-129-stage0-pays-*'

Statistics (plan §2-§3):
  prize  per population: mean over its signed bodies of (motif - base) at a = 6 (the `g<gen> +-1 base | delta` lines,
         as runs/RBT-125/gate/prize_readout.py parses them); over all 10 populations (a population without a ROW = 0,
         A1.2), mean and t(9) 95%.  Condition: lower bound > 0.
  steps  the `STEP <cell> | nose step w 3 -> 3.4 | ... | vs per-unit speed (n k): m [lo, hi] READING` field, as
         steps.py printed it.  Condition: NOSE LEADS or COMPARABLE.
  designed PAYS = both.
t quantiles: steps.py's own scipy-free t_ppf (copied from the 29ab80b blob), so the recomputations match the tool.
"""
import io
import json
import math
import os
import re
import subprocess
import sys
import tarfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LAUNCH = "29ab80b"
LEGS = ("prize", "steps")
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)  # RBT-90 part 2's ten populations (prize hosts)
EXTRA_TOOLS = ("runs/RBT-97/mechanism.py", "runs/RBT-97/resign_rbt67.py")  # DESIGN §12: verified post hoc
DELTA, R_MIN = 0.10, 1.10
NOSE_LINE = "nose step w 3 -> 3.4"


def git(*a, binary=False):
    out = subprocess.run(("git", "-C", ROOT) + a, check=True, capture_output=True).stdout
    return out if binary else out.decode()


# ---- steps.py's scipy-free t quantile (29ab80b:runs/RBT-125/gate/steps.py, blob 4834838), verbatim in substance --
def _betainc(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _betainc(b, a, 1.0 - x)
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        for num in (m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m)), -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))):
            d = 1.0 + num * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + num / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            break
    return front * h / a


def t_ppf(q, df):
    if q == 0.5:
        return 0.0
    if q < 0.5:
        return -t_ppf(1.0 - q, df)
    cdf = lambda t: 1.0 - 0.5 * _betainc(df / 2.0, 0.5, df / (df + t * t))
    lo, hi = 0.0, 1.0
    while cdf(hi) < q:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if cdf(mid) < q:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13:
            break
    return 0.5 * (lo + hi)


def t_int(x, level=0.95):
    x = np.asarray(x, float)
    if len(x) < 2:
        return (float(x.mean()) if len(x) else float("nan")), float("nan"), float("nan")
    hw = t_ppf(0.5 + level / 2, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return float(x.mean()), float(x.mean() - hw), float(x.mean() + hw)


def reading(d):
    """steps.py's reading(), the registered order (REGISTRATION.md §B, A1.4)."""
    m, lo, hi = t_int(d)
    _, lo90, hi90 = t_int(d, 0.90)
    if lo > 0:
        return "NOSE LEADS"
    if hi < 0:
        return "SPEED LEADS"
    if -DELTA < lo90 and hi90 < DELTA:
        return "COMPARABLE"
    return "TIED, UNRESOLVED"


def pays_steps(rd):
    return rd is not None and (rd.startswith("NOSE LEADS") or rd.startswith("COMPARABLE"))


def fmt(t):
    return f"{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]"


# ---- the launch records and the branches -------------------------------------------------------------------------
def launch(leg):
    txt = git("show", f"{LAUNCH}:runs/RBT-129/lanes/pays-{leg}/launch.txt")
    rec = {"tools": {}, "trees": {}}
    for ln in txt.splitlines():
        k, _, v = ln.partition(" ")
        if k == "cells":
            rec["cells"] = v.split()
        elif k.startswith("tool:"):
            rec["tools"][k[5:]] = v
        elif k.startswith("tree:"):
            rec["trees"][k[5:]] = v
        elif k in ("fair", "eat", "commit", "emitted", "runners", "procs"):
            rec[k] = v
    return rec


def branch(cell, leg):
    return f"origin/ckpt/rbt-129-stage0-pays-{cell}-{leg}"


def unpack(cell, leg):
    """{relative path: text} of the branch's snapshot, plus its MANIFEST and commit."""
    ref = branch(cell, leg)
    names = git("ls-tree", "--name-only", ref).split()
    parts = sorted(n for n in names if n.startswith("run.tar.gz.part"))
    blob = b"".join(git("cat-file", "blob", f"{ref}:{p}", binary=True) for p in parts)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        for m in tf.getmembers():
            if m.isfile():
                files[m.name] = tf.extractfile(m).read().decode()
    return {"files": files, "manifest": git("show", f"{ref}:MANIFEST").split("\n"), "sha": git("rev-parse", ref).strip(),
            "parts": len(parts)}


def config(cell):
    return json.loads(git("show", f"{LAUNCH}:runs/RBT-129/worlds/config/{cell}/config.json"))


# ---- parsers (prize_readout.py's for the prize; steps.py's print format for the steps) ----------------------------
def parse_prize(txt):
    if txt is None or not re.search(r"^ROW .*$", txt, re.M):
        return None
    body = {int(g): (int(s), float(b), float(d)) for g, s, b, d in
            re.findall(r"^g(\d+)\s+([+-]1)\s+(\d+\.\d+) \|\s+([+-]\d+\.\d+)\s*$", txt, re.M)}
    if not body:
        return None
    mot = re.search(r"^\s+motif\s+([+-]\d+\.\d+)", txt, re.M)
    dec = re.search(r"^\s+rotated decoy\s+([+-]\d+\.\d+)", txt, re.M)
    return {"body": body, "motif": float(mot.group(1)) if mot else None, "decoy": float(dec.group(1)) if dec else None,
            "row": re.search(r"^ROW .*$", txt, re.M).group(0),
            "world": (re.search(r"^WORLD CONTROL: .* world from (\S+)", txt, re.M) or [None, None])[1],
            "seeds": re.search(r"^(\d+) paired seeds from (\d+); w = \[(.*)\]", txt, re.M)}


def parse_steps(txt):
    out = {"fair": re.search(r"^# fairness: (.*)$", txt, re.M), "stepsrows": {}, "steps": {}, "r": {}}
    m = re.search(r"^# RBT-125 gate B: .* cell (\S+): (\{.*\})$", txt, re.M)
    out["label"], out["food"] = (m.group(1), json.loads(m.group(2))) if m else (None, None)
    m = re.search(r"^# world from (\S+); (\d+) paired seeds from (\d+)", txt, re.M)
    out["world"], out["nseeds"], out["seed0"] = (m.group(1), int(m.group(2)), int(m.group(3))) if m else (None, None, None)
    m = re.search(r"^# direction: (\d+) signed, (\d+) UNDETERMINED .*: (\[.*\])$", txt, re.M)
    out["signed"], out["und"], out["und_list"] = (int(m.group(1)), int(m.group(2)), m.group(3)) if m else (None, None, None)
    lines = txt.splitlines()
    hdr = next((i for i, ln in enumerate(lines) if ln.startswith("| host |")), None)
    out["host"] = {}
    if hdr is not None:
        cols = [c.strip() for c in lines[hdr].strip("|").split("|")]
        for ln in lines[hdr + 2:]:
            if not ln.startswith("| O1"):
                break
            v = [c.strip() for c in ln.strip("|").split("|")]
            out["host"][v[0]] = {c: float(x) for c, x in zip(cols[1:], v[1:])}
    num = r"([+-]\d+\.\d+) \[([+-]\d+\.\d+), ([+-]\d+\.\d+)\]"
    for ln in lines:
        m = re.match(r"^\| (.+?) \| " + num + r" \| " + num + r" \|$", ln)
        if m:
            out["steps"][m.group(1)] = tuple(float(x) for x in m.groups()[1:4]), tuple(float(x) for x in m.groups()[4:7])
        m = re.match(r"^  at w(\S+): r ([-+]?\d+\.\d+) \[([-+]?\d+\.\d+), ([-+]?\d+\.\d+)\], range (\S+)\.\.(\S+); (\d+) of (\d+) hosts .*"
                     r"per-unit speed step \(\+25% realised\) " + num + "$", ln)
        if m:
            g = m.groups()
            out["r"][g[0]] = {"r": tuple(map(float, g[1:4])), "range": (float(g[4]), float(g[5])), "in": int(g[6]),
                              "of": int(g[7]), "pu": tuple(map(float, g[8:11]))}
        m = re.match(r"^STEP (\S+) \| (.+?)\s+\| vs raw speed@w(\S+): " + num + r" (.+?) \| vs per-unit speed \(n (\d+)\): (.*)$", ln)
        if m:
            g = m.groups()
            pu = re.match(num + r" (.+)$", g[8])
            out["stepsrows"][g[1]] = {"cell": g[0], "raw": tuple(map(float, g[3:6])), "raw_reading": g[6], "n": int(g[7]),
                                      "pu": tuple(map(float, pu.groups()[:3])) if pu else None,
                                      "pu_reading": pu.group(4).strip() if pu else g[8].strip()}
    return out


# ---- step 1: integrity ---------------------------------------------------------------------------------------------
def integrity(P=print):
    ok = True
    recs = {leg: launch(leg) for leg in LEGS}
    P(f"# RBT-129 designed PAYS legs: integrity (plan §6 step 1).  Launch commit {LAUNCH} = {git('rev-parse', LAUNCH).strip()}\n")
    P("## blobs: every tool each leg pins, plus RBT-97's mechanism.py and resign_rbt67.py, against git rev-parse 29ab80b:<path>")
    seen = {}
    for leg in LEGS:
        for path, pin in recs[leg]["tools"].items():
            seen.setdefault(path, set()).add((leg, pin))
    for path in sorted(seen) + list(EXTRA_TOOLS):
        at = git("rev-parse", f"{LAUNCH}:{path}").strip()
        if path in seen:
            good = all(pin == at for _, pin in seen[path])
            legs = ",".join(sorted(leg for leg, _ in seen[path]))
            P(f"  {path:40s} pinned ({legs}) {sorted(p for _, p in seen[path])[0]}  29ab80b {at}  {'EQUAL' if good else 'MISMATCH'}")
        else:
            others = {c: git("rev-parse", f"{c}:{path}").strip() for c in (recs['prize']['commit'][:7], "origin/claude/new-session-4cao7d")}
            good = True  # not pinned by launch.txt: fixed by the runners' checkout of 29ab80b (DESIGN §12); reported
            P(f"  {path:40s} not pinned; 29ab80b {at}; at the emit commit {others[recs['prize']['commit'][:7]]}; "
              f"at integration {others['origin/claude/new-session-4cao7d']}  "
              f"{'EQUAL at all three' if len(set(others.values()) | {at}) == 1 else 'DIFFERS (fixed by the checkout)'}")
        ok &= good
    P("\n## pinned trees (launch.txt) against 29ab80b")
    for leg in LEGS:
        for path, pin in recs[leg]["trees"].items():
            at = git("rev-parse", f"{LAUNCH}:{path}").strip()
            ok &= pin == at
            P(f"  {leg:5s} {path:22s} pinned {pin}  29ab80b {at}  {'EQUAL' if pin == at else 'MISMATCH'}")
    P("\n## flags in launch.txt")
    for leg in LEGS:
        f_ok = recs[leg].get("fair") == "--fair" and recs[leg].get("eat") == "--eat-from root --eat-rule surface"
        ok &= f_ok
        P(f"  {leg}: fair {recs[leg].get('fair')!r}; eat {recs[leg].get('eat')!r}; {len(recs[leg]['cells'])} cells  {'OK' if f_ok else 'WRONG'}")
    if recs["prize"]["cells"] != recs["steps"]["cells"]:
        ok = False
        P("  the two legs' cell lists DIFFER")
    cells = recs["prize"]["cells"]
    P("\n## each cell's world at 29ab80b (worlds/config/<id>/config.json): fairness, eat_from, eat_rule, smell_contrast, smell_tau")
    cfgs = {}
    for c in cells:
        cfg = config(c)
        cfgs[c] = cfg
        f = cfg["sim"]["food"]
        good = cfg.get("fairness") == "fair" and f.get("eat_from") == "root" and f.get("eat_rule") == "surface"
        ok &= good
        P(f"  {c:14s} {cfg.get('fairness')!r:7s} {f.get('eat_from')} {f.get('eat_rule')} G {f.get('smell_contrast', 0)} tau {f.get('smell_tau', '-')}  "
          f"{'OK' if good else 'WRONG'}")
    P("\n## completeness and provenance, per cell (branch sha, MANIFEST, files)")
    P("prize: 10 outputs, each with its ROW, labelled <seed>-<cell>, bodies forage-<seed>, world = the cell's config, 64 seeds "
      "from 7000, w = [3]; the decoy at PW cells only.  steps: designed.txt with fairness 'fair', food = the cell's config, "
      "128 seeds from 125000, 3 STEP rows labelled with the cell.  .err: bytes (MuJoCo warnings).")
    rows_total = {"prize": 0, "steps": 0}
    errkinds = {}
    for c in cells:
        cfg_path = f"runs/RBT-129/worlds/config/{c}/config.json"
        for leg in LEGS:
            u = unpack(c, leg)
            man = u["manifest"]
            m_ok = man[0] == leg and man[3] == "consistent"
            errs = sum(len(v) for k, v in u["files"].items() if k.endswith(".err"))
            for k, v in u["files"].items():
                if k.endswith(".err"):
                    for ln in v.splitlines():
                        if ln.strip():
                            kind = re.sub(r"[-+]?\d[\d.e+-]*", "#", ln)[:90]
                            errkinds[kind] = errkinds.get(kind, 0) + 1
            stray = [k for k in u["files"] if k.endswith(".tmp")]
            if leg == "prize":
                probs = []
                n = 0
                for s in SEEDS:
                    txt = u["files"].get(f"prize/{s}.txt")
                    p = parse_prize(txt)
                    if p is None:
                        probs.append(f"{s}: no ROW")
                        continue
                    n += 1
                    if not p["row"].startswith(f"ROW {s}-{c}:"):
                        probs.append(f"{s}: ROW label")
                    if p["world"] != cfg_path:
                        probs.append(f"{s}: world {p['world']}")
                    if f"bodies from runs/RBT-129/bodies/forage-{s}," not in txt:
                        probs.append(f"{s}: bodies")
                    if not p["seeds"] or p["seeds"].groups() != ("64", "7000", "3"):
                        probs.append(f"{s}: seeds/w")
                    if ("-PW-" in c) != (p["decoy"] is not None):
                        probs.append(f"{s}: decoy {'missing' if '-PW-' in c else 'present'}")
                extra = sorted(k for k in u["files"] if not re.match(r"prize/(\d+)\.txt(\.err)?$", k))
                rows_total["prize"] += n
                good = m_ok and n == 10 and not probs and not stray
                P(f"  {c:14s} prize {u['sha'][:7]} {man[2]} {man[3]:10s} ROW {n}/10  .err {errs} B  "
                  f"{'; '.join(probs) or 'provenance OK'}{'; extra ' + str(extra) if extra else ''}  {'OK' if good else 'FAIL'}")
            else:
                txt = u["files"].get("steps/designed.txt")
                s = parse_steps(txt) if txt else None
                probs = []
                if s is None:
                    probs.append("no output")
                else:
                    if not s["fair"] or s["fair"].group(1) != "'fair'":
                        probs.append("fairness")
                    if s["food"] != cfgs[c]["sim"]["food"]:
                        probs.append("food block differs from the config")
                    if s["world"] != cfg_path:
                        probs.append(f"world {s['world']}")
                    if (s["nseeds"], s["seed0"]) != (128, 125000):
                        probs.append("seeds")
                    if s["label"] != c or any(r["cell"] != c for r in s["stepsrows"].values()):
                        probs.append("label")
                    if len(s["stepsrows"]) != 3:
                        probs.append(f"{len(s['stepsrows'])} STEP rows")
                extra = sorted(k for k in u["files"] if k not in ("steps/designed.txt", "steps/designed.txt.err"))
                nrows = len(s["stepsrows"]) if s else 0
                rows_total["steps"] += nrows
                good = m_ok and not probs and not stray
                P(f"  {c:14s} steps {u['sha'][:7]} {man[2]} {man[3]:10s} STEP {nrows}/3  signed {s['signed'] if s else '-'} "
                  f"UND {s['und'] if s else '-'}  .err {errs} B  {'; '.join(probs) or 'provenance OK'}"
                  f"{'; extra ' + str(extra) if extra else ''}  {'OK' if good else 'FAIL'}")
            ok &= good
    P("\n## .err lines over all 36 branches, by kind (digits replaced by #); anything but MuJoCo warnings would be a FAIL")
    for kind, n in sorted(errkinds.items(), key=lambda kv: -kv[1]):
        good = kind.startswith("WARNING:")
        ok &= good
        P(f"  {n:6d}  {kind}  {'(MuJoCo warning)' if good else 'NOT A WARNING'}")
    P(f"\nROW rows: {rows_total['prize']} of {10 * len(cells)}; STEP rows: {rows_total['steps']} of {3 * len(cells)}")
    P(f"\nINTEGRITY: {'PASS' if ok else 'FAIL -- HELP wake; nothing is read'}")
    return ok, cells


# ---- steps 2-5 ----------------------------------------------------------------------------------------------------
def prize_stats(pr):
    """pr: {seed: parsed or None} -> per-population prize (missing = 0), decoy diffs, base"""
    pop = {s: (float(np.mean([v[2] for v in p["body"].values()])) if p else 0.0) for s, p in pr.items()}
    dd = {s: ((p["motif"] - p["decoy"]) if p and p["decoy"] is not None else 0.0) for s, p in pr.items()}
    has_dec = any(p and p["decoy"] is not None for p in pr.values())
    base = float(np.mean([np.mean([v[1] for v in p["body"].values()]) for p in pr.values() if p]))
    signed = sum(len(p["body"]) for p in pr.values() if p)
    return pop, (dd if has_dec else None), base, signed


def per_host_lines(s):
    """from the per-host table: nose step w3 -> 3.4, raw speed@w3 step, r@w3, per host (3-decimal inputs)"""
    H = s["host"]
    nose = {h: v["w3.4"] - v["w3"] for h, v in H.items()}
    raw = {h: v["speed@w3"] - v["w3"] for h, v in H.items()}
    unit = {h: raw[h] * 0.25 / (H[h]["r@w3"] - 1.0) for h in H if H[h]["r@w3"] >= R_MIN}
    row = s["stepsrows"].get(NOSE_LINE)
    if row and len(unit) == row["n"] + 1:  # r printed "1.100" is below 1.10 unrounded when steps.py excluded it
        edge = [h for h in unit if round(H[h]["r@w3"], 3) == R_MIN]
        if len(edge) == 1:
            del unit[edge[0]]
            s.setdefault("edge", []).append(edge[0])
    return nose, raw, unit


def readout(cells, P=print):
    P("# RBT-129 designed PAYS legs: readout (READOUT-PLAN.md, pre-data at c47403c).  Integrity: PASS (integrity.txt)\n")
    P("Hosts are pre-fairness (RBT-125 harness adversary #443, S3): RBT-90 part 2's bests (prize) and RBT-113 O1's finals "
      "(steps) evolved without effector_bias_sigma = 0, so they carry the effector-bias walk. Every figure below is on them.\n")
    R = {}
    for c in cells:
        pu = unpack(c, "prize")
        pr = {s: parse_prize(pu["files"].get(f"prize/{s}.txt")) for s in SEEDS}
        st = parse_steps(unpack(c, "steps")["files"]["steps/designed.txt"])
        pop, dd, base, signed = prize_stats(pr)
        R[c] = {"pr": pr, "pop": pop, "dd": dd, "base": base, "signed": signed, "st": st,
                "prize": t_int(list(pop.values())), "ddt": t_int(list(dd.values())) if dd else None}
        row = st["stepsrows"].get(NOSE_LINE)
        R[c]["row"] = row
        R[c]["rd"] = row["pu_reading"] if row else "NOT READABLE"
        R[c]["c_prize"] = R[c]["prize"][1] > 0
        R[c]["c_steps"] = pays_steps(R[c]["rd"]) if row and row["pu"] else False
        R[c]["pays"] = R[c]["c_prize"] and R[c]["c_steps"]

    P("## 2. Per cell (p = 0.03).  prize: RBT-106's at a = 6, over 10 populations, t(9) 95%.  steps: the registered line, "
      "nose w 3 -> 3.4 minus the per-unit +25% speed step at w3, paired per host, t 95%, steps.py's reading.")
    P("   Beside it (coordinator 08:10): the nose step's own payoff and THE SPEED STEP'S OWN PAYOFF (per-unit at w3, and raw).\n")
    P("| cell | prize a=6 [t(9) 95%] | LB>0 | motif-decoy (PW; descr.) | nose-speed, per-unit (n) | reading | nose step w3->3.4 | "
      "per-unit speed step @w3 (n) | raw speed @w3 items (net) | r@w3 (range; out) | designed PAYS | flags |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        x, st, row = R[c], R[c]["st"], R[c]["row"]
        nose_t, nose_net = st["steps"].get(NOSE_LINE, (None, None))
        raw_t, raw_net = st["steps"].get("speed step at w3 (raw)", (None, None))
        r3 = st["r"].get("3")
        flags = []
        if x["rd"].startswith("NOSE LEADS") and (r3["pu"][2] < 0 or nose_t[1] <= 0):
            flags.append("lead carried by the speed step")
        if x["pays"] and x["ddt"] and x["ddt"][1] <= 0:
            flags.append("not shown food-dependent (decoy)")
        if x["c_prize"] and not x["ddt"]:
            flags.append("no decoy (U/HP)")
        P(f"| {c} | {fmt(x['prize'])} | {'yes' if x['c_prize'] else 'no'} | {fmt(x['ddt']) if x['ddt'] else '--'} | "
          f"{fmt(row['pu']) + ' (' + str(row['n']) + ')' if row and row['pu'] else '--'} | {x['rd']} | {fmt(nose_t)} | "
          f"{fmt(r3['pu'])} ({r3['in']}) | {fmt(raw_t)} ({raw_net[0]:+.3f}) | {r3['r'][0]:.2f} ({r3['range'][0]:.2f}..{r3['range'][1]:.2f}; "
          f"{r3['of'] - r3['in']}) | **{'PAYS' if x['pays'] else 'no'}** | {'; '.join(flags) or '-'} |")

    P("\n### beside the registered line (descriptive): raw-speed reading, w1 and first-nose readings (per-unit), signed hosts, "
      "base income, signed bodies")
    P("| cell | w3 vs raw speed | w1 -> 1.4 vs per-unit speed@w1 | first nose vs per-unit speed@w0 | installed a=6 - host | signed hosts | "
      "prize base income | bodies signed |")
    P("|---|---|---|---|---|---|---|---|")
    for c in cells:
        st = R[c]["st"]
        sr = st["stepsrows"]
        w1, f0 = sr.get("nose step w 1 -> 1.4"), sr.get("first nose (w 0 -> 0.4)")
        inst = st["steps"].get("installed a = 6 (w 3) - host", ((float("nan"),) * 3,))[0]
        P(f"| {c} | {fmt(sr[NOSE_LINE]['raw'])} {sr[NOSE_LINE]['raw_reading']} | "
          f"{(fmt(w1['pu']) + ' ' + w1['pu_reading']) if w1 and w1['pu'] else '--'} | "
          f"{(fmt(f0['pu']) + ' ' + f0['pu_reading']) if f0 and f0['pu'] else '--'} | {fmt(inst)} | {st['signed']} of {st['signed'] + st['und']} | "
          f"{R[c]['base']:.3f} | {R[c]['signed']}/70 |")

    P("\n### per population prize (items per season at a = 6), per cell")
    P("| cell | " + " | ".join(str(s) for s in SEEDS) + " |")
    P("|---|" + "---|" * len(SEEDS))
    for c in cells:
        P(f"| {c} | " + " | ".join(f"{R[c]['pop'][s]:+.3f}" if R[c]['pr'][s] else "MISSING(0)" for s in SEEDS) + " |")

    # marginals
    P("\n## 2b. Marginals (descriptive): counts over the cells in each level, mean prize, mean (nose - per-unit speed)")
    P("| factor | level | cells | PAYS | prize LB>0 | NOSE LEADS | COMPARABLE | TIED | SPEED LEADS | mean prize | mean nose-speed | mean per-unit speed step |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    fac = {"L": lambda c: c.split("-")[2], "s": lambda c: c.split("-")[3], "c": lambda c: c.split("-")[0]}
    for f, key in fac.items():
        for lev in sorted({key(c) for c in cells}, key=lambda v: ("U", "HP", "PW", "L", "G", "c0", "c1", "c2").index(v)):
            cs = [c for c in cells if key(c) == lev]
            cnt = lambda lab: sum(R[c]["rd"].startswith(lab) for c in cs)
            P(f"| {f} | {lev} | {len(cs)} | {sum(R[c]['pays'] for c in cs)} | {sum(R[c]['c_prize'] for c in cs)} | {cnt('NOSE LEADS')} | "
              f"{cnt('COMPARABLE')} | {cnt('TIED')} | {cnt('SPEED LEADS')} | {np.mean([R[c]['prize'][0] for c in cs]):+.3f} | "
              f"{np.mean([R[c]['row']['pu'][0] for c in cs]):+.3f} | {np.mean([R[c]['st']['r']['3']['pu'][0] for c in cs]):+.3f} |")
    tot = len(cells)
    P(f"| all | - | {tot} | {sum(R[c]['pays'] for c in cells)} | {sum(R[c]['c_prize'] for c in cells)} | "
      f"{sum(R[c]['rd'].startswith('NOSE LEADS') for c in cells)} | {sum(R[c]['rd'].startswith('COMPARABLE') for c in cells)} | "
      f"{sum(R[c]['rd'].startswith('TIED') for c in cells)} | {sum(R[c]['rd'].startswith('SPEED LEADS') for c in cells)} | "
      f"{np.mean([R[c]['prize'][0] for c in cells]):+.3f} | {np.mean([R[c]['row']['pu'][0] for c in cells]):+.3f} | "
      f"{np.mean([R[c]['st']['r']['3']['pu'][0] for c in cells]):+.3f} |")

    P("\n## 3. Holistic PAYS and the holistic nose step: NOT RUN (blocked; LEGS.md B1-B4). The PAYS layer is designed-fauna only.")

    # 4. descriptive comparison with RBT-125's gate
    P("\n## 4. Descriptive comparison (no verdicts): RBT-125's gate (committed eating rule, no --fair, RBT-90 random terrain) "
      "against these cells (the sweep's block).  G2.5 <-> s = G; G0 <-> s = L.  Paired by population (prize) or host (steps); "
      "differences are printed, not tested.")
    gate = os.path.join(ROOT, "runs", "RBT-125", "gate")
    P("\n### prize at a = 6, t(9) 95%")
    P("| RBT-125 cell | RBT-125 prize | RBT-129 c0 | RBT-129 c1 | RBT-129 c2 | c0 - gate, paired by population |")
    P("|---|---|---|---|---|---|")
    for L in ("U", "HP", "PW"):
        for g, s in (("G2.5", "G"), ("G0", "L")):
            gp = {k: parse_prize(open(os.path.join(gate, "prize", f"{L}-{g}-{k}.txt")).read())
                  if os.path.exists(os.path.join(gate, "prize", f"{L}-{g}-{k}.txt")) else None for k in SEEDS}
            gpop, _, _, _ = prize_stats(gp)
            cs = [f"c{i}-p030-{L}-{s}" for i in range(3)]
            P(f"| {L}-{g} | {fmt(t_int(list(gpop.values())))} | " + " | ".join(fmt(R[c]['prize']) for c in cs) +
              f" | {fmt(t_int([R[cs[0]]['pop'][k] - gpop[k] for k in SEEDS]))} |")
    P("\n### §B registered line (nose w3 -> 3.4 minus per-unit speed@w3), and the per-unit speed step at w3, t 95%")
    P("| RBT-125 cell | gate: nose - speed (n), reading | gate: per-unit speed @w3 | RBT-129 cell | here: nose - speed (n), reading | "
      "here: per-unit speed @w3 | here - gate, nose - speed, paired by host (n) |")
    P("|---|---|---|---|---|---|---|")
    for g, s in (("G2.5", "G"), ("G0", "L")):
        gs = parse_steps(open(os.path.join(gate, "steps", f"PW-{g}.txt")).read())
        grow = gs["stepsrows"][NOSE_LINE]
        gn, _, gu = per_host_lines(gs)
        for i in range(3):
            c = f"c{i}-p030-PW-{s}"
            hn, _, hu = per_host_lines(R[c]["st"])
            common = [h for h in hu if h in gu]
            d = [(hn[h] - hu[h]) - (gn[h] - gu[h]) for h in common]
            row = R[c]["row"]
            P(f"| PW-{g} | {fmt(grow['pu'])} ({grow['n']}), {grow['pu_reading']} | {fmt(gs['r']['3']['pu'])} | {c} | "
              f"{fmt(row['pu'])} ({row['n']}), {R[c]['rd']} | {fmt(R[c]['st']['r']['3']['pu'])} | {fmt(t_int(d))} ({len(d)}) |")

    # 5. robustness
    P("\n## 5. Robustness: leave-one-out lower bounds (as the RBT-125 pass-2 adversary did)")
    P("Check first: the registered line recomputed from the per-host table (3-decimal inputs) against the STEP row as printed.")
    P("| cell | STEP row (per-unit) | recomputed from the table | reading, recomputed | match |")
    P("|---|---|---|---|---|")
    for c in cells:
        hn, _, hu = per_host_lines(R[c]["st"])
        d = [hn[h] - hu[h] for h in hu]
        rc = t_int(d)
        row = R[c]["row"]
        match = len(d) == row["n"] and all(abs(a - b) < 0.006 for a, b in zip(rc, row["pu"])) and reading(d) == R[c]["rd"].split(" (")[0]
        edge = R[c]["st"].get("edge")
        note = f"; host {edge[0]} at printed r 1.100 left out, as steps.py's n says" if edge else ""
        P(f"| {c} | {fmt(row['pu'])} (n {row['n']}) {R[c]['rd']} | {fmt(rc)} (n {len(d)}) | {reading(d)} | {'yes' if match else 'NO'}{note} |")
    P("\n| cell | PAYS | prize LB, leave one population out: min .. max (population at min) | prize flips? | "
      "steps LB, leave one host out: min .. max | readings reached | steps flips? | PAYS call flips? |")
    P("|---|---|---|---|---|---|---|---|")
    fragile = []
    for c in cells:
        x = R[c]
        lo = {s: t_int([x["pop"][k] for k in SEEDS if k != s])[1] for s in SEEDS}
        smin = min(lo, key=lo.get)
        pflip = [s for s in SEEDS if (lo[s] > 0) != x["c_prize"]]
        hn, _, hu = per_host_lines(x["st"])
        d = {h: hn[h] - hu[h] for h in hu}
        hl, rds = {}, {}
        for h in d:
            rest = [d[k] for k in d if k != h]
            hl[h], rds[h] = t_int(rest)[1], reading(rest)
        sflip = [h for h in d if pays_steps(rds[h]) != x["c_steps"]]
        callflip = []
        for s in SEEDS:  # one omission at a time, in either leg; the other leg keeps its full-sample call
            if ((lo[s] > 0) and x["c_steps"]) != x["pays"]:
                callflip.append(f"pop {s}")
        for h in d:
            if (x["c_prize"] and pays_steps(rds[h])) != x["pays"]:
                callflip.append(f"host {h.replace('/U/conventional/final/', '/').replace('.json', '')}")
        if callflip:
            fragile.append((c, callflip))
        P(f"| {c} | {'PAYS' if x['pays'] else 'no'} | {lo[smin]:+.3f} .. {max(lo.values()):+.3f} ({smin}) | "
          f"{'YES: ' + ','.join(map(str, pflip)) if pflip else 'no'} | {min(hl.values()):+.3f} .. {max(hl.values()):+.3f} | "
          f"{', '.join(sorted(set(rds.values())))} | {'YES (' + str(len(sflip)) + ' hosts)' if sflip else 'no'} | "
          f"{'**FRAGILE**: ' + ', '.join(callflip) if callflip else 'no'} |")
    P(f"\nFRAGILE: PAYS calls, either way, that flip under a single omission: {len(fragile)} of {len(cells)}")
    for c, cf in fragile:
        P(f"  {c}: {', '.join(cf)}")

    # headline
    n_pays = sum(R[c]["pays"] for c in cells)
    P("\n## HEADLINE (computed)")
    P(f"designed PAYS at {n_pays} of {len(cells)} cells: {', '.join(c for c in cells if R[c]['pays']) or 'none'}")
    P(f"prize lower bound > 0 at {sum(R[c]['c_prize'] for c in cells)} of {len(cells)}; steps NOSE LEADS or COMPARABLE at "
      f"{sum(R[c]['c_steps'] for c in cells)} of {len(cells)}")
    P("holistic PAYS and the holistic nose step: NOT RUN (blocked). Hosts pre-fairness (#443 S3). No multiplicity correction "
      "(none registered; 18 cells x 2 conditions).")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "integrity"
    buf = io.StringIO()
    P = lambda *a: print(*a, file=buf)
    ok, cells = integrity(P if mode == "readout" else print)
    if mode == "integrity":
        return 0 if ok else 1
    if not ok:
        print(buf.getvalue())
        print("refusing: integrity failed")
        return 1
    readout(cells)
    return 0


if __name__ == "__main__":
    sys.exit(main())
