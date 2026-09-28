"""RBT-129: readout of the steps leg re-measured at the 12 c >= 1 cells (`steps2`), under READOUT-PLAN.md (this directory).

    python runs/RBT-129/legs-readout-steps2/steps2_readout.py integrity DIR > runs/RBT-129/legs-readout-steps2/integrity.txt
    python runs/RBT-129/legs-readout-steps2/steps2_readout.py readout DIR   > runs/RBT-129/legs-readout-steps2/steps2_readout.txt

DIR holds one directory per cell, each restored with
`scripts/durable.sh restore DIR/<cell> rbt-129-stage0-pays-<cell>-steps2` (so DIR/<cell>/designed.txt).

The registered line (plan §2) is the per-unit field of each cell's `STEP <cell> | nose step w 3 -> 3.4` line. The prize
condition is #467's, read from `runs/RBT-129/legs-readout/legs_readout.txt`. `t_int` and `reading` are taken from
`steps.py` at the pinned blob (not re-implemented), for the leave-one-host-out check (plan §5).
"""
import ast
import os
import re
import subprocess
import sys

import numpy as np

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
STEPS_BLOB = "d4b91bf3170d21b78528b5c5ee6690469ba2f90c"
SEED0 = 126000
LAUNCH = "runs/RBT-129/lanes/pays-steps-c1c2/launch.txt"
CELLS = [f"c{c}-p030-{L}-{s}" for L in ("U", "HP", "PW") for s in ("L", "G") for c in (1, 2)]
NUM = r"([+-]?\d+\.\d+)"
IV = rf"{NUM} \[{NUM}, {NUM}\]"


def steps_funcs():
    """t_int, reading and DELTA from steps.py at the pinned blob"""
    src = subprocess.run(["git", "cat-file", "blob", STEPS_BLOB], capture_output=True, text=True, cwd=ROOT).stdout
    tree = ast.parse(src)
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("_betainc", "t_ppf", "t_int", "reading")]
    keep += [n for n in tree.body if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "DELTA" for t in n.targets)]
    ns = {"np": np, "math": __import__("math")}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "steps.py@d4b91bf", "exec"), ns)
    return ns["t_int"], ns["reading"]


def parse(path):
    txt = open(path).read()
    d = {"txt": txt, "step": {}, "steps": {}, "at": {}, "cross": {}, "rtab": [], "host": {}}
    for m in re.finditer(r"^STEP (\S+) \| (.+?)\s+\| vs raw speed@w\S+ \(descriptive, n (\d+)\): (.+?) \| vs per-unit speed "
                         r"\(n (\d+); (\d+) out for > 25% exploded\): (.+)$", txt, re.M):
        cell, label, nraw, raw, n, out, pu = m.groups()
        d["step"][label] = dict(cell=cell, nraw=int(nraw), raw=raw.strip(), n=int(n), out=int(out), pu=pu.strip())
    for m in re.finditer(rf"^\| ((?:first nose|nose step|installed|speed step)[^|]*?) \| (\d+) \((\d+) out\) \| {IV} \| {IV} \|$", txt, re.M):
        d["steps"][m.group(1)] = dict(n=int(m.group(2)), out=int(m.group(3)), items=tuple(map(float, m.group(4, 5, 6))))
    for m in re.finditer(r"^  at w(\d): (\d+) host\(s\) out for > 25% exploded; r ([\d.]+) \[([\d.]+), ([\d.]+)\], range ([\d.]+)\.\.([\d.]+); "
                         rf"(\d+) of (\d+) hosts at r >= 1.10 enter the per-unit comparison; per-unit speed step \(\+25% realised\) (.+)$", txt, re.M):
        w = m.group(1)
        d["at"][w] = dict(out=int(m.group(2)), r=tuple(map(float, m.group(3, 4, 5))), rng=(float(m.group(6)), float(m.group(7))),
                          enter=int(m.group(8)), ins=int(m.group(9)), unit=m.group(10).strip())
    for m in re.finditer(r"^  at w(\d): mean and median r on opposite sides of 1.10: (.+)$", txt, re.M):
        d["cross"][m.group(1)] = m.group(2).strip()
    for m in re.finditer(r"^\| (O1/\S+) \| (\d) \| ([\d.na]+) \| ([\d.na]+) \| ([\d.-]+) \| ([\d.-]+) \|$", txt, re.M):
        d["rtab"].append(dict(host=m.group(1), w=m.group(2), rmed=float(m.group(3)), rmean=float(m.group(4)),
                              mxf=float(m.group(5)) if m.group(5) != "--" else float("nan"),
                              mxs=float(m.group(6)) if m.group(6) != "--" else float("nan")))
    hdr = re.search(r"^\| host \| (.+) \| exploded seasons per arm \((.+)\) \|$", txt, re.M)
    cols = [c.strip() for c in hdr.group(1).split("|")] if hdr else []
    for line in txt.splitlines():
        f = [x.strip() for x in line.strip().strip("|").split("|")]
        if hdr and line.startswith("| O1/") and len(f) == len(cols) + 2:
            d["host"][f[0]] = dict(zip(cols, map(float, f[1:-1])), boom=list(map(int, f[-1].split())))
    m = re.search(r"^  exploded seasons per arm, all hosts: (.+)$", txt, re.M)
    d["boom_all"] = m.group(1) if m else None
    m = re.search(r"^# direction: (\d+) signed, (\d+) UNDETERMINED", txt, re.M)
    d["signed"], d["undet"] = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    m = re.search(r"^# hosts: (\d+) ", txt, re.M)
    d["hosts"] = int(m.group(1)) if m else None
    return d


def prize467():
    """{cell: (prize text, LB > 0)} from #467's legs_readout.txt §2 table (first row per cell)"""
    out = {}
    for line in open(os.path.join(ROOT, "runs/RBT-129/legs-readout/legs_readout.txt")):
        m = re.match(rf"^\| (c\d-p030-\w+-\w) \| ({IV}) \| (yes|no) \|", line)
        if m and m.group(1) not in out:
            out[m.group(1)] = (m.group(2), m.group(6) == "yes")
    return out


def label(pu):
    """the READING of a per-unit field"""
    if pu.endswith("NOT READABLE"):
        return "NOT READABLE"
    for k in ("NOSE LEADS", "SPEED LEADS", "COMPARABLE", "TIED, UNRESOLVED"):
        if k in pu:
            return k
    return "NOT READABLE"


def verdict(prize_ok, lab):
    if not prize_ok:
        return "not PAYS (prize)"
    if lab in ("NOSE LEADS", "COMPARABLE"):
        return "PAYS"
    if lab == "NOT READABLE":
        return "UNDECIDED (not readable)"
    return "not PAYS (unresolved)" if lab.startswith("TIED") else f"not PAYS ({lab})"


def meanr_line(d, t_int, reading):
    """descriptive only (#475 ruling; #488 SHOULD 3): the per-unit line rebuilt from the per-host table with hosts entering
    at MEAN r >= 1.10 instead of median r. Approximate, for the pairing reason in plan §5"""
    rows = {r["host"]: r for r in d["rtab"] if r["w"] == "3"}
    v = [(x["w3.4"] - x["w3"]) - (x["speed@w3"] - x["w3"]) * 0.25 / (rows[h]["rmean"] - 1.0)
         for h, x in d["host"].items() if h in rows and rows[h]["rmean"] >= 1.10]
    if len(v) < 2:
        return "-- NOT READABLE (n %d)" % len(v)
    return f"{f3(t_int(v))} (n {len(v)}) {reading(v).split(' (')[0]}"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT).stdout.strip()


def integrity(base):
    ok = True
    launch = open(os.path.join(ROOT, LAUNCH)).read()
    cells = re.search(r"^cells (.+)$", launch, re.M).group(1).split()
    print(f"# RBT-129 steps2 integrity (READOUT-PLAN.md, this directory); launch record {LAUNCH}")
    print(f"launch cells: {len(cells)}; equal to the 12 c >= 1 PAYS cells: {sorted(cells) == sorted(CELLS)}")
    ok &= sorted(cells) == sorted(CELLS)
    tool = re.search(r"^tool:runs/RBT-125/gate/steps.py (\w+)$", launch, re.M).group(1)
    flags = re.search(r"^flags (.+)$", launch, re.M).group(1)
    print(f"launch tool:steps.py {tool}; == {STEPS_BLOB[:7]}: {tool == STEPS_BLOB}")
    print(f"launch flags: {flags!r}; has --seed0 {SEED0} and --exclude-exploded: {f'--seed0 {SEED0}' in flags and '--exclude-exploded' in flags}")
    print(f"launch fair: {'fair --fair' in launch}; eat root/surface: {'eat --eat-from root --eat-rule surface' in launch}")
    ok &= tool == STEPS_BLOB and f"--seed0 {SEED0}" in flags and "--exclude-exploded" in flags and "fair --fair" in launch
    for r in sorted(os.listdir(os.path.join(ROOT, os.path.dirname(LAUNCH)))):
        if r.startswith("runner"):
            s = open(os.path.join(ROOT, os.path.dirname(LAUNCH), r)).read()
            jobs = re.findall(r"python runs/RBT-125/gate/steps.py \S+ (\S+) .*?--seed0 (\d+) --exclude-exploded", s)
            g = f'git hash-object runs/RBT-125/gate/steps.py)" = "{STEPS_BLOB}"' in s
            print(f"{r}: blob guard on {STEPS_BLOB[:7]} (exit 6): {g}; jobs {len(jobs)}, all --seed0 {SEED0}: {all(j[1] == str(SEED0) for j in jobs)}")
            ok &= g and all(j[1] == str(SEED0) for j in jobs)
    print(f"steps.py at HEAD: {git('rev-parse', 'HEAD:runs/RBT-125/gate/steps.py')[:7]}; at 5cbb2be (#480 head): "
          f"{git('rev-parse', '5cbb2be:runs/RBT-125/gate/steps.py')[:7]}")
    heads = git("ls-remote", "origin", "refs/heads/ckpt/rbt-129-stage0-pays-*-steps2")
    print("\n| cell | branch | MANIFEST | STEP lines (w0, w1, w3) | cell label | fair | world | seeds | signed / hosts | out >25% (w3 line) | exploded seasons per arm (all hosts) | total |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in CELLS:
        br = f"ckpt/rbt-129-stage0-pays-{c}-steps2"
        has = f"refs/heads/{br}" in heads
        man = git("show", f"origin/{br}:MANIFEST").splitlines() if has else []
        p = os.path.join(base, c, "designed.txt")
        d = parse(p) if os.path.exists(p) else None
        if not d:
            print(f"| {c} | {has} | -- | MISSING | | | | | | | | |")
            ok = False
            continue
        labs = ["first nose (w 0 -> 0.4)", "nose step w 1 -> 1.4", "nose step w 3 -> 3.4"]
        nstep = sum(l in d["step"] for l in labs)
        cellok = all(d["step"][l]["cell"] == c for l in labs if l in d["step"])
        fair = "# fairness: 'fair'" in d["txt"]
        world = f"# world from runs/RBT-129/worlds/config/{c}/config.json; 128 paired seeds from {SEED0}" in d["txt"]
        tot = sum(int(x.split()[-1]) for x in d["boom_all"].split(",")) if d["boom_all"] else -1
        w3 = d["step"].get("nose step w 3 -> 3.4", {})
        print(f"| {c} | {has} | {man[3] if len(man) > 3 else '?'} | {nstep}/3 | {cellok} | {fair} | {world} | {'128 from 126000' if world else '?'} | "
              f"{d['signed']} / {d['hosts']} | {w3.get('out', '?')} | {d['boom_all']} | {tot} |")
        ok &= has and nstep == 3 and cellok and fair and world and (len(man) > 3 and man[3] == "consistent")
    print(f"\nINTEGRITY: {'PASS' if ok else 'FAIL'}")


def f3(t):
    return f"{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]"


def loo(d, t_int, reading):
    """leave one host out of the registered per-unit line, reconstructed from the per-host table (plan §5)"""
    lab = "nose step w 3 -> 3.4"
    st = d["step"][lab]
    rows = {r["host"]: r for r in d["rtab"] if r["w"] == "3"}
    # hosts in the line: not out for > 25% exploded (not identifiable per host from the file when out > 0), r >= 1.10
    if st["out"] or d["at"]["3"]["out"]:
        return None, "not reconstructable (hosts out for > 25% exploded are not named per line)"
    vals = {}
    for h, x in d["host"].items():
        if h in rows and rows[h]["rmed"] >= 1.10:
            vals[h] = (x["w3.4"] - x["w3"]) - (x["speed@w3"] - x["w3"]) * 0.25 / (rows[h]["rmed"] - 1.0)
    if len(vals) != st["n"]:
        return None, f"not reconstructable (host count {len(vals)} != n {st['n']})"
    full = t_int(list(vals.values()))
    m = re.match(IV, st["pu"])
    reg = tuple(map(float, m.groups())) if m else None
    if reg is None or max(abs(a - b) for a, b in zip(full, reg)) > 0.01:
        return None, f"not reconstructable (reconstructed {f3(full)} vs registered {st['pu'][:26]})"
    reads = {}
    for h in vals:
        rest = [v for k, v in vals.items() if k != h]
        reads.setdefault(reading(rest).split(" (")[0], []).append(h)
    return reads, f"reconstructed {f3(full)} (registered {st['pu'][:26]})"


def readout(base):
    t_int, reading = steps_funcs()
    prize = prize467()
    print("# RBT-129 steps2 readout (READOUT-PLAN.md, this directory). Registered line: per-unit field of `nose step w 3 -> 3.4`")
    print("\n## 1. Per cell: the registered line, its label, the prize (#467), the verdict\n")
    print("| cell | prize [t(9) 95%] (#467) | LB > 0 | nose − speed, per-unit (n; out >25%) | label | verdict | mean-r line, reconstructed (descriptive, #475) |")
    print("|---|---|---|---|---|---|---|")
    D, V = {}, {}
    for c in CELLS:
        p = os.path.join(base, c, "designed.txt")
        d = D[c] = parse(p) if os.path.exists(p) else None
        st = d["step"].get("nose step w 3 -> 3.4") if d else None
        lab = label(st["pu"]) if st else "NOT READABLE"
        V[c] = verdict(prize[c][1], lab)
        print(f"| {c} | {prize[c][0]} | {'yes' if prize[c][1] else 'no'} | {re.match(IV, st['pu']).group(0) if st and lab != 'NOT READABLE' else '--'}"
              f"{' (' + str(st['n']) + '; ' + str(st['out']) + ')' if st else ''} | {lab} | **{V[c]}** | {meanr_line(d, t_int, reading)} |")
    print("\n## 2. Beside the line (descriptive): the r line at w3 (median r), mean r, max kept path speed, crossing hosts, raw line\n")
    print("| cell | hosts signed | out >25% (r line) | r median: mean [t 95%] (range) | enter at r >= 1.10 | per-unit speed step @w3 | mean of mean-r | max kept path speed (speed arm / base arm) | median/mean r cross 1.10 | raw line (n) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for c in CELLS:
        d = D[c]
        a = d["at"].get("3") if d else None
        st = d["step"].get("nose step w 3 -> 3.4") if d else None
        rt = [r for r in d["rtab"] if r["w"] == "3"] if d else []
        mr = np.nanmean([r["rmean"] for r in rt]) if rt else float("nan")
        mxf = np.nanmax([r["mxf"] for r in rt]) if rt else float("nan")
        mxs = np.nanmax([r["mxs"] for r in rt]) if rt else float("nan")
        cross = d["cross"].get("3", "?") if d else "?"
        cross = "none" if cross == "none" else f"{len(cross.split(', '))}: " + ", ".join(x.replace("/conventional/final/", "/").replace(".json", "") for x in cross.split(", "))
        print(f"| {c} | {d['signed']} | {a['out']} | {a['r'][0]:.3f} [{a['r'][1]:.3f}, {a['r'][2]:.3f}] ({a['rng'][0]:.2f}..{a['rng'][1]:.2f}) | "
              f"{a['enter']} of {a['ins']} | {a['unit']} | {mr:.3f} | {mxf:.3f} / {mxs:.3f} | {cross} | {st['raw']} ({st['nraw']}) |")
    print("\n## 3. The steps themselves (items, t 95%, hosts in; out) and the other per-unit lines (descriptive)\n")
    print("| cell | nose step w3 -> 3.4 | raw speed step @w3 | 'lead carried by the speed step' | first nose, per-unit | w 1 -> 1.4, per-unit |")
    print("|---|---|---|---|---|---|")
    for c in CELLS:
        d = D[c]
        ns, sp = d["steps"]["nose step w 3 -> 3.4"], d["steps"]["speed step at w3 (raw)"]
        st = d["step"]["nose step w 3 -> 3.4"]
        unit = re.match(IV, d["at"]["3"]["unit"])
        flag = "--"
        if label(st["pu"]) == "NOSE LEADS":
            flag = "yes" if (unit and float(unit.group(3)) < 0) or ns["items"][1] <= 0 else "no"
        print(f"| {c} | {f3(ns['items'])} ({ns['n']}; {ns['out']}) | {f3(sp['items'])} ({sp['n']}; {sp['out']}) | {flag} | "
              f"{d['step']['first nose (w 0 -> 0.4)']['pu']} | {d['step']['nose step w 1 -> 1.4']['pu']} |")
    print("\n## 4. Robustness: leave one host out of the registered line (plan §5)\n")
    for c in CELLS:
        reads, note = loo(D[c], t_int, reading)
        lab = label(D[c]["step"]["nose step w 3 -> 3.4"]["pu"])
        if reads is None:
            print(f"- {c}: {note}")
            continue
        flips = {k: v for k, v in reads.items() if (k in ("NOSE LEADS", "COMPARABLE")) != (lab in ("NOSE LEADS", "COMPARABLE"))}
        fr = "; FRAGILE: " + "; ".join(f"{k} without {', '.join(h.replace('/conventional/final/', '/').replace('.json', '') for h in v)}"
                                      for k, v in flips.items()) if flips and prize467()[c][1] else ""
        print(f"- {c}: {note}; readings reached: " + ", ".join(f"{k} ×{len(v)}" for k, v in sorted(reads.items())) + fr)
    print("\n## 5. Verdicts\n")
    for k in ("PAYS", "not PAYS", "UNDECIDED"):
        cs = [c for c in CELLS if V[c].startswith(k)]
        print(f"{k}: {len(cs)}: {', '.join(cs) if cs else '--'}")


if __name__ == "__main__":
    {"integrity": integrity, "readout": readout}[sys.argv[1]](sys.argv[2])
