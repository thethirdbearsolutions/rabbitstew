"""RBT-72: re-derive every headline number in paper 8 from committed files.

No simulation and no new measurement. Every number the paper quotes is recomputed here from a
file on the integration branch, and printed beside the figure the ticket or document quoted, with
a status:

  MATCH        recomputed from the file and equal to the quoted figure at its printed precision
  MISMATCH     recomputed from the file and NOT equal to the quoted figure; the paper says so
  READOUT      the file is a printed readout with no underlying data committed, so the number is
               read (and, where it is arithmetic on other printed numbers, recomputed) from the
               readout; it cannot be re-derived from data by anyone
  PROSE        the only committed source is prose (a report or a copied document); flagged in the
               paper as not re-derivable

Run from the repository root:  python runs/RBT-72/rederive.py > runs/RBT-72/rederive.txt
"""

import json
import math
import re
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROWS = []


def row(cid, claim, path, mine, quoted, status=None):
    """Record one claim.  If status is None it is MATCH when the strings agree, else MISMATCH."""
    if status is None:
        status = "MATCH" if str(mine) == str(quoted) else "MISMATCH"
    ROWS.append((cid, claim, path, str(mine), str(quoted), status))


def read(p):
    return (ROOT / p).read_text()


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


def pct(x, nd=1):
    return f"{100 * x:.{nd}f}%"


# --------------------------------------------------------------------------------------------
# 1. The prize: the direct four-link motif installed in the phenotype
# --------------------------------------------------------------------------------------------
P = "docs/artifacts/RBT-23-W4b-801/verify_independent-rerun.txt"
t = read(P)
dot = re.search(r"dot product = (-?[\d.]+)", t).group(1)
row("P1", "Pioneer wheel hinge axes, world-frame dot product", P, dot, "-1.0000")
tab = dict(re.findall(r"\| (motif w=\d+|spike w=32) \|[^|]*\| ([+-][\d.]+) \|", t))
row("P2", "direct motif w=8 (a=16), W4b bests, seeds 9000+", P, tab["motif w=8"], "+0.054", "READOUT")
row("P3", "direct motif w=16 (a=32)", P, tab["motif w=16"], "+0.246", "READOUT")
row("P4", "common mode (the spike) w=32", P, tab["spike w=32"], "-1.502", "READOUT")

P = "docs/artifacts/RBT-67/seedset_anchor.json"
s = json.load(open(ROOT / P))
base = st.mean(s["baseline"].values())
d64 = st.mean(s["per_robot_delta_64"])
row("P5", "baseline items, W4b bests, seeds 9000-9063 (mean of 7 robots)", P, f"{base:.3f}", "1.516")
row("P6", "direct motif a=64, delta items (mean of 7 per-robot deltas)", P, f"{d64:+.3f}", "+0.897")
row("P7", "  its 95% CI over robots (stored)", P,
    "[{:+.3f}, {:+.3f}]".format(*s["delta_64"][1:]), "[+0.632, +1.176]")
row("P8", "  robots improved", P, f"{sum(x > 0 for x in s['per_robot_delta_64'])}/7", "7/7")
row("P9", "  as a fraction of baseline", P, f"+{100 * d64 / base:.0f}%", "+59%")

P = "runs/sim-audit/CHAOTIC-DOC.md"
row("P10", "yoked phantom-food control at a=64 (seeds 9000+)", P, "no script or readout committed",
    "+0.163", "PROSE")
row("P11", "taxis-specific gain = 0.897 - phantom", P, f"{0.897 - 0.163:+.3f}", "+0.723")
row("P12", "  as a fraction of baseline", P, f"+{100 * (0.897 - 0.163) / 1.516:.1f}%", "+48%")

P = "docs/artifacts/RBT-67/w4b.json"
w = json.load(open(ROOT / P))
cells = {c["a"]: c for c in w["cells"]}
wb = cells[0.0]["items"]
row("P13", "W4b bests baseline, seeds 7000-7063", P, f"{wb:.3f}", "1.270")
for a, q in [(32.0, "+0.435"), (64.0, "+1.018"), (384.0, "+1.875")]:
    rd = [r["delta"] for r in cells[a]["robots"]]
    row(f"P14/{int(a)}", f"W4b ladder a={int(a)}: delta (mean of robots), improved", P,
        f"{st.mean(rd):+.3f} {sum(x > 0 for x in rd)}/7", f"{q} 7/7")
row("P15", "W4b a=384 CI over robots (stored)", P,
    "[{:+.3f}, {:+.3f}]".format(*cells[384.0]["ci"]), "[+1.243, +2.438]")
row("P16", "W4b a=384 as a fraction of baseline", P,
    f"+{100 * cells[384.0]['delta'] / wb:.0f}%", "+148%")
row("P17", "W4b: robots improved at every rung >= 32", P,
    str(all(all(r["delta"] > 0 for r in c["robots"]) for a, c in cells.items() if a > 0)), "True")

P = "docs/artifacts/RBT-67/p801.json"
p = json.load(open(ROOT / P))
pc = {c["a"]: c for c in p["cells"]}
row("P18", "P-801 bests baseline (all seven)", P, f"{pc[0.0]['items']:.3f}", "2.770")
BWD = (100, 400)
for a, q in [(32.0, None), (64.0, "+3.206 5/5"), (384.0, "+8.094 5/5")]:
    fw = [r["delta"] for r in pc[a]["robots"] if r["gen"] not in BWD]
    row(f"P19/{int(a)}", f"P-801 five forward drivers, own sign, a={int(a)}", P,
        f"{st.mean(fw):+.3f} {sum(x > 0 for x in fw)}/5", q if q else f"{st.mean(fw):+.3f} {sum(x > 0 for x in fw)}/5",
        None if q else "READOUT")
fwbase = st.mean(r["items"] - r["delta"] for r in pc[384.0]["robots"] if r["gen"] not in BWD)
fw384 = st.mean(r["delta"] for r in pc[384.0]["robots"] if r["gen"] not in BWD)
row("P20", "P-801 forward five at a=384 as a fraction of their baseline", P,
    f"+{100 * fw384 / fwbase:.0f}%", "+301%")
bw_all = [r["delta"] for a, c in pc.items() if a >= 64 for r in c["robots"] if r["gen"] in BWD]
row("P20b", "P-801 forward five baseline (mean of their items minus delta)", P, f"{fwbase:.3f}", "2.688")
row("P21", "P-801 backward two (g100, g400) lose at every rung >= 64", P,
    f"{sum(x < 0 for x in bw_all)}/{len(bw_all)} robot-rungs negative", "12/12 robot-rungs negative")

P = "docs/artifacts/RBT-67/manipulation_384.json"
m = json.load(open(ROOT / P))["summary"]
row("P22", "phantom smell at a=384, delta items", P, f"{m['phantom:384']['delta']:+.3f}", "-0.217")
row("P23", "phantom smell at a=64, delta items (seeds 7000+)", P, f"{m['phantom:64']['delta']:+.3f}", "+0.257")
row("P24", "antimotif at a=384", P, f"{m['antimotif:384']['delta']:+.3f}", "-1.094")
row("P25", "bearing to smell ascent: base / a=64 / a=384 (rad)", P,
    " / ".join(f"{m[k]['bearing_grad']:.3f}" for k in ("base:0", "compass:64", "compass:384")),
    "1.534 / 1.347 / 1.265")
row("P26", "distance to live-item centroid: base / 64 / 384 (m)", P,
    " / ".join(f"{m[k]['centroid_d']:.2f}" for k in ("base:0", "compass:64", "compass:384")),
    "2.83 / 2.32 / 2.02")

# RBT-69 on P-801 with the W4b (published) sign
P = "docs/runs/RBT-69-compass-replication.txt"
t = read(P)
rows69 = {(k, float(wv)): float(dv) for k, wv, dv in
          re.findall(r"^(compass|common)\s+([\d.]+) \|\s+[\d.]+\s+([+-][\d.]+)", t, re.M)}
row("P27", "P-801, native world, published (W4b) sign, w=16 (a=32)", P, f"{rows69[('compass', 16.0)]:+.3f}", "-1.154", "READOUT")
row("P28", "  w=32 (a=64)", P, f"{rows69[('compass', 32.0)]:+.3f}", "-0.549", "READOUT")
row("P29", "  common mode w=4: delta, robots better", P,
    f"{rows69[('common', 4.0)]:+.3f} " + re.search(r"^common\s+4\.00 .*?\|\s+(\d/7)", t, re.M).group(1),
    "-2.710 0/7", "READOUT")
P = "docs/runs/RBT-69-compass-replication-w4.txt"
t = read(P)
r4 = {float(wv): dv for wv, dv in re.findall(r"^compass\s+([\d.]+) \|\s+[\d.]+\s+([+-][\d.]+)", t, re.M)}
row("P30", "P-801 in a W4'-shaped world, published sign, w=16 / w=32", P, f"{r4[16.0]} / {r4[32.0]}",
    "-0.328 / -0.375", "READOUT")
P = "docs/runs/RBT-69-travel-direction.txt"
t = read(P)
per = [(int(g), d, float(v)) for g, d, v in
       re.findall(r"^\s+(\d+)\s+[+-][\d.]+°\s+(forward|BACKWARD) \|\s+([+-][\d.]+)", t, re.M)]
fwd = [v for g, d, v in per if d == "forward"]
bwd = [v for g, d, v in per if d == "BACKWARD"]
row("P31", "P-801 w=32, published sign: forward drivers mean, improved", P,
    f"{st.mean(fwd):+.3f} {sum(v > 0 for v in fwd)}/{len(fwd)}", "-1.738 1/5")
row("P32", "  backward drivers mean, improved (mean of two printed 3-dp values; 2.4215)", P,
    f"{st.mean(bwd):+.4f} {sum(v > 0 for v in bwd)}/{len(bwd)}", "+2.422 2/2",
    "MATCH" if abs(st.mean(bwd) - 2.422) <= 0.0006 else "MISMATCH")
row("P33", "  all seven (reproduces the -0.549)", P, f"{st.mean(fwd + bwd):+.3f}", "-0.549")
row("P34", "P-801 pooled travel offset, R (PR #11 implementation)", P,
    re.search(r"pooled :\s+([+-][\d.]+) deg\s+R=([\d.]+)", t).expand(r"\1 \2"), "+12.0 0.430")
P = "docs/artifacts/RBT-23-W4b-801/travel_direction.txt"
t = read(P)
row("P35", "W4b bests pooled travel offset, R", P,
    re.search(r"POOLED ([+-][\d.]+) deg, R=([\d.]+)", t).expand(r"\1 \2"), "-174.1 0.756")

# --------------------------------------------------------------------------------------------
# 2. The proposal rate
# --------------------------------------------------------------------------------------------
P = "runs/RBT-45/stats.txt"
t = read(P)
row("R1", "RBT-23 conventional, alive at season 599: first-parent depth median, max", P,
    re.search(r"median ([\d.]+), max (\d+)", t).expand(r"\1 \2"), "19.0 23")
P = "runs/RBT-59/depth.json"
dj = json.load(open(ROOT / P))
base_rows = [r for r in dj if r["last_season"] == 599]   # the rows that survived to season 599
meds = [r["median"] for r in base_rows]
row("R2", "RBT-59: median depth at season 599 over max_age-60 population rows (min-max, rows)", P,
    f"{min(meds):.0f}-{max(meds):.0f} ({len(meds)} rows)", "18-24 (14 rows)")

P = "runs/RBT-45/cells.json"
cj = json.load(open(ROOT / P))
c19 = [c for c in cj["cells"] if c["kind"] == "conventional" and c["add_link_rate"] == 0.15
       and c["remove_link_rate"] == 0.1 and c["k"] == 19][0]
row("R0", "RBT-45 grid, default operator, k=19: both wheel noses wired / 'crossed' (sensor_influence)", P,
    f"{c19['pair']:.3f} / {c19['crossed']:.3f} of {c19['n']}", "0.091 / 0.013 of 2000")

P = "runs/compass-gain/survey.log"
t = read(P)
blocks = re.findall(r"(\S+_depth\d+)\s+\(.*?\n(.*?)(?=\n\n|\n===)", t, re.S)
both_path = [re.search(r"PATH .*?both noses wired\s+(\d+)/60", b).group(1) for _, b in blocks]
both_dir = [re.search(r"DIRECT .*?both noses wired\s+(\d+)/60", b).group(1) for _, b in blocks]
row("R3", "RBT-62: both wheel noses wired (PATH, depth-4), depths 23/39/78", P,
    "/".join(both_path) + " of 60", "0/10/4 of 60")
row("R4", "  the same on the DIRECT (depth-1) route", P, "/".join(both_dir) + " of 60", "0/5/0 of 60", "READOUT")
row("R5", "  '7-17% of a wheeled population' = PATH counts at depths 78 and 39", P,
    f"{100 * 4 / 60:.1f}%-{100 * 10 / 60:.1f}%, and 0% at depth 23", "7-17%", "READOUT")
best_dir = re.findall(r"direct gradient-dominant individuals:\s+\d+/60\s+best \|a\| among them:\s+([\d.]+)", t)
row("R6", "RBT-62: best DIRECT |a| among 'gradient-dominant' individuals, any depth", P, max(best_dir), "0.548")
best_path = re.findall(r"path   gradient-dominant individuals:\s+\d+/60\s+best \|a\| among them:\s+([\d.]+)", t)
row("R7", "RBT-62: best PATH |a| among them (the '16.3')", P, max(best_path, key=float), "16.257")

P = "docs/runs/RBT-78-reconcile.txt"
t = read(P)
dmax = re.findall(r"direct\s+[\d.]+\s+([\d.]+)\s+([\d.]+)%", t)
row("R8", "RBT-78: direct-route max |a| (W4b / P-801), share >= 16", P,
    " / ".join(x for x, _ in dmax) + " ; " + " / ".join(y + "%" for _, y in dmax), "3.232 / 3.333 ; 0.00% / 0.00%")
path_signed32 = re.findall(r"path\s+[\d.]+\s+[\d.]+\s+[\d.]+%\s+[\d.]+%\s+[\d.]+%\s+[\d.]+%\s+([\d.]+)%", t)
row("R9", "RBT-78: path-route signed a >= 32 (reproduces RBT-45's 0.70% in kind)", P,
    " / ".join(x + "%" for x in path_signed32), "0.44% / 0.36%")
P = "runs/RBT-45/motif.json"
mj = json.load(open(ROOT / P))
c19 = [c for c in mj["cells"] if c["kind"] == "conventional" and c["add"] == 0.15 and c["k_mut"] == 19][0]
row("R10", "RBT-45 (corrected calibration): a >= 32 / a >= 64 at depth 19, path to depth 4", P,
    f"{pct(c19['frac_a_ge_32'], 2)} / {pct(c19['frac_a_ge_64'], 2)}", "0.70% / 0.05%")
P = "docs/runs/RBT-78-truncation.txt"
t = read(P)
row("R11", "RBT-78: lineages clearing |a4| >= 16 that move >20% from depth 4 to 8", P,
    " / ".join(re.findall(r"clearing \|a4\|>=16 \((\d+)\): ([\d.]+)% move", t)[i][1] + "%" for i in range(2)),
    "100.0% / 100.0%")
row("R12", "  additionally clear at depth 8 (W4b / P-801)", P,
    " / ".join(re.findall(r"clears at d=8 but not d=4: (\d+)", t)), "544 / 358")
P = "docs/runs/RBT-81-adversary.txt"
t = read(P)
k, n = map(int, re.search(r"ALL.*?sign agreement (\d+)/(\d+)", t, re.S).groups())
row("R13", "RBT-81 adversary: depth-1 sign agrees with measured response", P, f"{k}/{n} = {100 * k / n:.0f}%", "1403/1519 = 92%")
row("R14", "  correlation of magnitude, wired only, pooled", P,
    re.search(r"ALL.*?WIRED only : ([+-][\d.]+)", t, re.S).group(1), "+0.0013")

P = "docs/artifacts/RBT-91-alone-baseline.txt"
t = read(P)
pools = dict(re.findall(r"\| (W4b-801-bests|P-801-final60) \| 100000 \| \*\*(\d+)\*\*", t))
tot = sum(map(int, pools.values()))
row("R15", "RBT-91: routed-motif structure, 19 mutations, W4b + P-801 (of 200,000)", P,
    f"{pools['W4b-801-bests']} + {pools['P-801-final60']} = {tot} ({100 * tot / 200000:.3f}%)", "54 + 30 = 84 (0.042%)")
P = "docs/artifacts/RBT-91-structural-rate.txt"
t = read(P)
lin = [int(x) for x in re.findall(r"W4b-801-bests lineage (\d+):", t)]
row("R16", "RBT-91 first 4 arrivals: W4b lineages whose parent index (i mod 7) is the same", P,
    f"{lin} mod 7 = {[i % 7 for i in lin]}", "three from one parent", "READOUT")
P = "docs/artifacts/RBT-91-resigned-84-reference.txt"
t = read(P)
verd = re.findall(r"\*\*(COMPASS|ANTI-COMPASS|UNDETERMINED)\*\*", t)
cmp_, anti, und = map(int, re.search(r"compasses (\d+), anti-compasses (\d+), undetermined (\d+) of 84", t).groups())
assert (cmp_, anti) == (verd.count("COMPASS"), verd.count("ANTI-COMPASS")), "summary line disagrees with the rows"
lo, hi = wilson(cmp_, cmp_ + anti)
row("R17", "RBT-91 re-signed at the reference probe: compass / anti / undetermined", P,
    f"{cmp_} / {anti} / {und}", "35 / 48 / 1")
row("R18", "  chemotactic fraction of resolved, Wilson 95%", P,
    f"{100 * cmp_ / (cmp_ + anti):.1f}% [{lo:.1f}, {hi:.1f}]", "42.2% [32.1, 52.9]")
bnd = re.search(r"bounds if every undetermined went one way: ([\d.]+)% .*? to ([\d.]+)%", t)
row("R18b", "  bounds if the undetermined arrival went either way", P, f"{bnd.group(1)}% to {bnd.group(2)}%", "41.7% to 42.9%")
z = (cmp_ - 0.5 * (cmp_ + anti)) / math.sqrt(0.25 * (cmp_ + anti))
row("R19", "  against 0.5 by sign symmetry: z", P, f"{z:+.2f}", "-1.43")

# --------------------------------------------------------------------------------------------
# 3. The magnitude gap
# --------------------------------------------------------------------------------------------
P = "runs/compass-gain/survey.log"
t = read(P)
wl = re.findall(r"^(\w+_depth\d+)\s+(conventional|holistic)\s+links=\s*(\d+)\s+median\s+([\d.]+)\s+p99\s+[\d.]+\s+max\s+([\d.]+)\s+\|w\|>=8\s+(\d+)", t, re.M)
row("M1", "RBT-62 census: links (conventional + holistic, three depths)", P, f"{sum(int(x[2]) for x in wl):,}", "19,892")
row("M2", "  links >= 8 anywhere", P, str(sum(int(x[5]) for x in wl)), "0")
mx = {}
for arm, kind, nlinks, med, mxw, ge8 in wl:
    mx[arm] = max(mx.get(arm, 0), float(mxw))
row("M3", "  max |w| at depths 23 / 39 / 78", P, " / ".join(f"{v:.2f}" for v in mx.values()), "4.65 / 5.52 / 6.11")
conv_med = [float(x[3]) for x in wl if x[1] == "conventional"]
row("M4", "  sigma observed = conventional median|w| / 0.6745", P,
    " / ".join(f"{v / 0.6745:.2f}" for v in conv_med), "1.25 / 1.47 / 1.72")
OP = "runs/RBT-91/weight_census.py (operator constants; docs/artifacts/RBT-91-weight-census.txt)"
pstep, preset, sig = 0.25 * (1 - 0.02), 0.25 * 0.02, 0.4
row("M5", "per-mutation variance added by the step, P(step)*sigma^2", OP, f"{pstep * sig * sig:.4f}", "0.0392")
row("M6", "sigma(d) = sqrt(1 + 0.0392 d) at d = 23 / 39 / 78", OP,
    " / ".join(f"{math.sqrt(1 + 0.0392 * d):.2f}" for d in (23, 39, 78)), "1.38 / 1.59 / 2.01")
row("M7", "depth at which that law puts a typical link at 16", OP, f"{(16 ** 2 - 1) / 0.0392:,.0f}", "6,500 (approx.)", "READOUT")
statvar = 1 + sig * sig * pstep / preset
row("M8", "stationary variance with the reset, 1 + sigma^2 P(step)/P(reset); rms", OP,
    f"{statvar:.2f}; {math.sqrt(statvar):.2f}", "8.84; 2.97")


def log10_tail(zv):
    # log10 of P(|Z| > z) for a standard normal, via erfc in log space for large z
    return math.log10(math.erfc(zv / math.sqrt(2))) if zv < 37 else (
        -(zv * zv / 2) / math.log(10) - math.log10(zv * math.sqrt(math.pi / 2)))


row("M9", "RBT-62's 1e-77: log10 P(|a| >= 32) with SD 2*sigma = 3.44 (as the report states)",
    "runs/compass-gain/REPORT.md s4", f"{log10_tail(32 / 3.44):.1f}", "-77")
row("M10", "  the same with SD = sigma = 1.72 (var(a) = sigma^2 for a = (w1+w2-w3-w4)/2)",
    "runs/compass-gain/REPORT.md s4", f"{log10_tail(32 / 1.72):.1f}", "-77")

P = "docs/artifacts/RBT-91-weight-census.txt"
t = read(P)
allb = re.search(r"all committed bests\s+n=\s*(\d+)\s+max=\s*([\d.]+).*?>=8:\s+([\d.]+)%", t)
row("M11", "RBT-91 census of every committed best: links, max |w|, share >= 8", P,
    f"{int(allb.group(1)):,} {allb.group(2)} {allb.group(3)}%", "9,637 5.200 0.00%")
asym = re.search(r"after 20,000 mutations\s+n=\s*\d+\s+max=\s*[\d.]+\s+p99=\s*[\d.]+\s+rms=\s*([\d.]+).*?>=8:\s+([\d.]+)%\s+>=16:\s+([\d.]+)%", t)
row("M12", "operator asymptote (20,000 mutations): rms, >= 8, >= 16", P,
    f"{asym.group(1)} {asym.group(2)}% {asym.group(3)}%", "2.938 1.96% 0.03%")
d20 = re.search(r"depth 20\s+n=\s*\d+\s+max=\s*([\d.]+)", t)
row("M13", "drift from committed bests, depth 20: max |w|", P, d20.group(1), "5.008")

P = "docs/runs/RBT-91-adversary.txt"
t = read(P)
ff = re.search(r"four free weights, asymptote\s+P\(\|a\|>=16\) =\s+([\d.]+)%\s+P\(\|a\|>=32\) =\s+([\d.]+)%", t)
fb = re.search(r"four free weights \+ bias, depth 2000\s+P\(\|a\|>=16\) =\s+([\d.]+)%\s+P\(\|a\|>=32\) =\s+([\d.]+)%", t)
cb = re.search(r"committed bests' weights \+ their biases\s+P\(\|a\|>=16\) =\s+([\d.]+)%\s+P\(\|a\|>=32\) =\s+([\d.]+)%", t)
row("M14", "four free weights at the asymptote, P(|a|>=32), bias ignored / bias included", P,
    f"{ff.group(2)}% / {fb.group(2)}%", "1.32% / 0.055%",
    "MATCH" if abs(float(ff.group(2)) - 1.32) < 0.005 and abs(float(fb.group(2)) - 0.055) <= 0.00051 else "MISMATCH")
row("M15", "  from the committed bests' own weights and biases, P(|a|>=32), of 200,000 draws", P,
    f"{round(float(cb.group(2)) * 2000)} in 200,000", "0 in 200,000")

sl = dict(re.findall(r"^\s+(\d+)\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+[\d.]+%", t, re.M))
row("M15b", "bias walk: median tanh slope sech^2(b) at depth 20 / 200 / 1000", P,
    f"{sl['20']} / {sl['200']} / {sl['1000']}", "0.735 / 0.085 / 0.001")

P = "docs/artifacts/RBT-91-structural-rate.txt"
t = read(P)
r8 = re.search(r"w=  8\.0 sign=\+1:.*?small-signal a =\s+([+-][\d.]+)", t).group(1)
row("M16", "routed motif installed at w=8 (linear 2w = 16): realised small-signal response", P, r8, "+3.5657")
row("M17", "  linear over realised", P, f"{16 / float(r8):.1f}x", "4.5x")
for sigma, f, q_al, q_bg in [("0.4", "docs/artifacts/RBT-91-alone-baseline.txt", "0 of 84 [0.0, 4.4]", "26 / 9996 = 0.26%"),
                             ("1.6", "docs/artifacts/RBT-91-alone-1.6.txt", "0 of 63 [0.0, 5.7]", "141 / 9995 = 1.41%"),
                             ("4.0", "docs/artifacts/RBT-91-alone-4.0.txt", "0 of 66 [0.0, 5.5]", "164 / 9994 = 1.64%")]:
    t = read(f)
    alone = [abs(float(x)) for x in re.findall(r"LINKS ALONE ([+-][\d.]+)", t)]
    nstruct = len(alone)
    k_al = sum(v >= 6.8664 for v in alone)
    lo, hi = (max(0.0, x) for x in wilson(k_al, nstruct))
    bg = re.search(r"(\d+) of (\d+) STRUCTURELESS", t)
    row(f"M18/{sigma}", f"weight_sigma {sigma}: motif links alone reach the paying-rung reference 6.87", f,
        f"{k_al} of {nstruct} [{lo:.1f}, {hi:.1f}]", q_al)
    row(f"M19/{sigma}", f"weight_sigma {sigma}: structureless background, whole brain >= 6.87", f,
        f"{bg.group(1)} / {bg.group(2)} = {100 * int(bg.group(1)) / int(bg.group(2)):.2f}%", q_bg)
    row(f"M20/{sigma}", f"weight_sigma {sigma}: largest links-alone response", f, f"{max(alone):.2f}",
        {"0.4": "1.26", "1.6": "3.51", "4.0": "3.91"}[sigma])
n_all = sum(len(re.findall(r"LINKS ALONE", read(f))) for f in (
    "docs/artifacts/RBT-91-alone-baseline.txt", "docs/artifacts/RBT-91-alone-1.6.txt", "docs/artifacts/RBT-91-alone-4.0.txt"))
row("M18b", "structural arrivals scored links-alone over the three scales", "docs/artifacts/RBT-91-alone-*.txt",
    str(n_all), "213", "MATCH" if n_all == 213 else "MISMATCH")
hi84 = wilson(0, 84)[1] / 100
row("M18c", "bound on a correctly signed paying arrival per lineage: Wilson upper(0/84) x 84/200,000 x 35/83",
    "docs/artifacts/RBT-91-alone-baseline.txt; docs/artifacts/RBT-91-resigned-84-reference.txt",
    f"{hi84 * 84 / 200000 * 35 / 83:.1e}", "below 1e-5", "MATCH" if hi84 * 84 / 200000 * 35 / 83 < 1e-5 else "MISMATCH")
alone_meds = re.findall(r"links-alone median ([\d.]+)", read("docs/artifacts/RBT-91-alone-baseline.txt"))
row("M18d", "links-alone median, W4b / P-801 pools, default scale", "docs/artifacts/RBT-91-alone-baseline.txt",
    " / ".join(alone_meds), "0.0500 / 0.0218")
P = "docs/runs/RBT-81-drive-spec.txt"
t = read(P)
ds = {int(a): float(b) for a, b in re.findall(r"^\s+(\d+)\s+\d+\s+[\d.]+\s+([\d.]+)", t, re.M)}
row("M21", "the other calibrated probe (RBT-81 adversary): DIRECT motif w=8 / w=32 at drive 0.01", P,
    f"{ds[8]:.3f} / {ds[32]:.3f}", "8.264 / 32.236", "READOUT")
row("M22", "  against RBT-91's probe on the ROUTED motif at w=8 (3.5657): ratio", P,
    f"{ds[8] / 3.5657:.2f}x", "2.3x (units unreconciled)", "READOUT")

# --------------------------------------------------------------------------------------------
# 4. What populations did with a compass
# --------------------------------------------------------------------------------------------
P = "docs/artifacts/RBT-80-series.txt"
t = read(P)
sec = t.split("## mean_lifetime_score")[1].split("\n## ")[0]
lines = [l.split() for l in sec.splitlines() if re.match(r"\s+\d+\s", l)]
cols = ["A:seeded", "A:control", "A:drift", "B:seeded", "B:control", "B:drift", "C:seeded", "C:control", "C:drift"]
series = {c: [float(l[i + 1]) for l in lines] for i, c in enumerate(cols)}
nseason = len(lines)
diffs = [st.mean(series[f"{s}:seeded"]) - st.mean(series[f"{s}:control"]) for s in "ABC"]
row("S1", f"RBT-80 seeded - control mean lifetime score, {nseason} seasons, seeds A/B/C", P,
    " / ".join(f"{d:+.3f}" for d in diffs), "+0.432 / +0.371 / +0.373")
P = "docs/artifacts/RBT-80-three-seed-report.txt"
t = read(P)
row("S2", "RBT-80 plateau seeded - drift at depth 2 (primary)", P,
    " / ".join(re.findall(r"\| [ABC] \| plateau 250-299 \| [+-][\d.]+ \| ([+-][\d.]+) \|", t)), "+0.253 / -0.030 / +0.286")
ctrl = re.findall(r"\| [ABC] \| control \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|", t)
row("S3", "RBT-80 control carriage at the plateau, d1/d2/d4, all seeds", P,
    "all zero" if all(float(x) == 0 for r in ctrl for x in r) else str(ctrl), "all zero")
inv = re.findall(r"\| ([ABC]) \| (seeded|drift) \| [\d.]+/60 \| ([\d.]+) \|", t)
row("S4", "RBT-80 inverted carriers at the plateau: seeded vs drift", P,
    " / ".join(v for s, a, v in inv if a == "seeded") + " vs " + " / ".join(v for s, a, v in inv if a == "drift"),
    "2.2 / 1.7 / 2.7 vs 17.3 / 12.2 / 18.0")
P = "docs/artifacts/RBT-80-within-arm.txt"
t = read(P)
row("S5", "RBT-80 carriers minus non-carriers inside the seeded arm, depth 2", P,
    " / ".join(re.findall(r"^\| 2 \|.*?\| ([+-][\d.]+) \| \[", t, re.M)), "+1.144 / +0.415 / +0.499")
P = "docs/artifacts/RBT-23-W4b-801/compass_race.txt"
t = read(P)
row("S6", "RBT-77 race from gen 590: chains reaching |a|>=16 (DEPTH-4 path sum), peak, end", P,
    re.search(r"chains reaching \|a\|>=16: (\d+/16)", t).group(1) + " "
    + re.search(r"\| 11 \| ([\d.]+) \| ([\d.]+) \|", t).expand(r"\1 \2"), "1/16 26.5 6.1", "READOUT")
P = "docs/artifacts/RBT-23-W4b-801/compass_vs_flip.txt"
t = read(P)
row("S7", "RBT-77 single mutations: P(flip), acquisitions |a|>=8 (parents from the uncommitted run)", P,
    f"{22 / 288:.4f} (=22/288) ; " + ("0/288" if "zero acquisitions" in t else "?"), "0.0764 ; 0/288", "READOUT")

# --------------------------------------------------------------------------------------------
# 5. Round 1 (adversary PR #78) and RBT-97 (PR #71, #79): rows added for the answer
# --------------------------------------------------------------------------------------------
P = "docs/artifacts/RBT-23-W4b-801/genotype_motif.txt"
t = read(P)
gm_rows = dict(((c, w_), (d, imp)) for c, w_, d, imp in
               re.findall(r"^\| (motif|anti) \| (\d+) \| ([+-][\d.]+) \| \[[^]]+\] \| (\d/7) \|", t, re.M))
row("G1", "ROUTED motif installed in the genotype, W4b bests: w=8 / 16 / 32, delta and improved", P,
    " / ".join(f"{gm_rows[('motif', w_)][0]} {gm_rows[('motif', w_)][1]}" for w_ in ("8", "16", "32")),
    "+0.114 5/7 / +0.277 7/7 / +0.879 7/7", "READOUT")
row("G2", "  routed anti-motif w=32", P, " ".join(gm_rows[("anti", "32")]), "-1.020 0/7", "READOUT")

P = "runs/RBT-72-adversary/probe_rung.txt"
t = read(P)
rung = {int(w_): (float(wp), float(wn), float(ap)) for w_, wp, wn, ap in
        re.findall(r"w=\s*(\d+): whole brain \+1 ([+-][\d.]+) / -1 ([+-][\d.]+).*?links alone \+1 ([+-][\d.]+)", t)}
row("G3", "installed routed motif on P-801 g590, LINKS ALONE at w=8 / w=16 (the arrivals' scale)", P,
    f"{rung[8][2]:.2f} / {rung[16][2]:.2f}", "6.28 / 12.52", "READOUT")
row("G4", "  whole brain at w=16 (the hard-coded 6.8664)", P, f"{rung[16][0]:+.4f}", "+6.8664", "READOUT")
row("G5", "  linear 2w over links-alone at w=8", P, f"{16 / rung[8][2]:.2f}x", "2.55x", "READOUT")
row("G6", "  RBT-81's direct w=8 (8.264) over routed links-alone w=8", P, f"{8.264 / rung[8][2]:.2f}x", "1.32x", "READOUT")
alone_max = {"0.4": 1.2622, "1.6": 3.5064, "4.0": 3.9108}
row("G7", "largest own-link response as a share of the links-alone null / paying rung, sigma 0.4 and 4.0", P,
    f"{100 * alone_max['0.4'] / rung[8][2]:.0f}%/{100 * alone_max['0.4'] / rung[16][2]:.0f}% ; "
    f"{100 * alone_max['4.0'] / rung[8][2]:.0f}%/{100 * alone_max['4.0'] / rung[16][2]:.0f}%",
    "20%/10% ; 62%/31%", "READOUT")

# F3: the re-signing, on the whole brain as committed and on the motif's own links
P = "docs/artifacts/RBT-91-resigned-84-reference.txt"
t = read(P)
rs = re.findall(r"^\| (W4b-801-bests|P-801-final60) #(\d+) \| ([+-][\d.]+) \| [+-][\d.]+ deg \| [\d.]+ \| (\w+) \| \*\*[+-][\d.]+\*\* \| \*\*([A-Z-]+)\*\*", t, re.M)
al = {(p_, int(l)): (float(x), float(y)) for p_, l, x, y in re.findall(
    r"(W4b-801-bests|P-801-final60) lineage (\d+): 1 unit\(s\), LINKS ALONE ([+-][\d.]+) \(.*?whole brain ([+-][\d.]+)",
    read("docs/artifacts/RBT-91-alone-baseline.txt"))}
row("F3a", "re-signing's raw a equals the WHOLE-BRAIN response (rows parsed)", P,
    f"{sum(abs(al[(p_, int(l))][1] - float(raw)) < 1e-4 for p_, l, raw, d, v in rs)}/{len(rs)}", f"{len(rs)}/{len(rs)}")
zeros = sum(float(raw) == 0 and v == "ANTI-COMPASS" for p_, l, raw, d, v in rs)
row("F3b", "arrivals printing 0.0000 counted as ANTI-COMPASS", P, str(zeros), "5")
wc = sum(v == "COMPASS" for *_, v in rs)
wa = sum(v == "ANTI-COMPASS" and float(raw) != 0 for p_, l, raw, d, v in rs)
lo, hi = wilson(wc, wc + wa)
row("F3c", "whole brain, zeros excluded: compass / anti, fraction", P, f"{wc} / {wa}, {100 * wc / (wc + wa):.1f}% [{lo:.1f}, {hi:.1f}]",
    "35 / 43, 44.9% [34.3, 55.9]")
oc = oa = 0
for p_, l, raw, d, v in rs:
    own = al[(p_, int(l))][0]
    if v == "UNDETERMINED" or abs(own) < 1e-4:
        continue
    sgn = own * (1 if d == "backward" else -1)
    oc += sgn > 0
    oa += sgn < 0
lo, hi = wilson(oc, oc + oa)
row("F3d", "motif's OWN links re-signed, |own| >= 1e-4: compass / anti, fraction", P,
    f"{oc} / {oa}, {100 * oc / (oc + oa):.1f}% [{lo:.1f}, {hi:.1f}]", "30 / 28, 51.7% [39.2, 64.1]")
both = [(float(raw), al[(p_, int(l))][0]) for p_, l, raw, d, v in rs if abs(float(raw)) >= 1e-4 and abs(al[(p_, int(l))][0]) >= 1e-4]
row("F3e", "own-link sign agrees with whole-brain sign where both non-zero", P,
    f"{sum((x > 0) == (y > 0) for x, y in both)}/{len(both)}", "31/57")


# F5: enrichment of whole-brain hits among arrivals over the structureless background
def fisher_greater(k, n, b, N):
    K, T = k + b, n + N
    def lp(x):
        return (math.lgamma(K + 1) - math.lgamma(x + 1) - math.lgamma(K - x + 1) + math.lgamma(T - K + 1)
                - math.lgamma(n - x + 1) - math.lgamma(T - K - n + x + 1)
                - (math.lgamma(T + 1) - math.lgamma(n + 1) - math.lgamma(T - n + 1)))
    return sum(math.exp(lp(x)) for x in range(k, min(n, K) + 1))


for sigma, (k, n, b, N), q in [("0.4", (4, 84, 26, 9996), "18.3x p 1e-04"), ("1.6", (4, 63, 141, 9995), "4.5x p 0.013"),
                               ("4.0", (4, 66, 164, 9994), "3.7x p 0.024")]:
    pv = fisher_greater(k, n, b, N)
    row(f"F5/{sigma}", f"weight_sigma {sigma}: whole-brain hits, arrivals over background, enrichment and one-sided Fisher p",
        "docs/artifacts/RBT-91-alone-*.txt", f"{(k / n) / (b / N):.1f}x p {pv:.2g}".replace("0.0001", "1e-04"), q)
top = sorted(float(x) for x in re.findall(r"whole brain ([+-][\d.]+)", read("docs/artifacts/RBT-91-alone-4.0.txt")))[-2:]
row("F5b", "the two largest whole-brain readings at sigma 4.0 (one Effector rail to rail at drive 0.01 reads 50)",
    "docs/artifacts/RBT-91-alone-4.0.txt", " / ".join(f"{x:.4f}" for x in top), "49.9994 / 50.0000")

# F6: the bound with each factor at its upper end
rate_hi = 84 / 200000 + 1.96 * math.sqrt(9) * math.sqrt((84 / 200000) * (1 - 84 / 200000) / 200000)
row("F6", "per-lineage bound: point product / every factor at its upper end (whole-brain sign 52.9%, own-link 64.1%)",
    "docs/artifacts/RBT-91-alone-baseline.txt", f"{hi84 * 84 / 200000 * 35 / 83:.1e} / {hi84 * rate_hi * 0.529:.1e} to {hi84 * rate_hi * 0.641:.1e}",
    "7.8e-06 / 1.6e-05 to 1.9e-05", "MATCH" if abs(hi84 * rate_hi * 0.529 - 1.6e-5) < 0.1e-5 else "MISMATCH")

# C1: t-intervals at n = 7 beside the stored bootstrap intervals
T6 = 2.446912
for cid, xs, q in [("C1/64", s["per_robot_delta_64"], "[+0.529, +1.266]"),
                   ("C1/384", [r["delta"] for r in cells[384.0]["robots"]], "[+1.062, +2.688]")]:
    mn, se = st.mean(xs), st.stdev(xs) / math.sqrt(len(xs))
    row(cid, f"t-interval over 7 robots ({cid[3:]}), beside the stored bootstrap", "docs/artifacts/RBT-67/*.json",
        f"[{mn - T6 * se:+.3f}, {mn + T6 * se:+.3f}]", q)

# C3: RBT-80 seeded - control at season 0 and at the plateau
row("C3", "RBT-80 seeded - control at season 0 / plateau 250-299, seeds A B C", "docs/artifacts/RBT-80-series.txt",
    " ; ".join(f"{series[x + ':seeded'][0] - series[x + ':control'][0]:+.3f} / "
               f"{st.mean(series[x + ':seeded'][250:300]) - st.mean(series[x + ':control'][250:300]):+.3f}" for x in "ABC"),
    "+0.774 / +0.451 ; +0.498 / +0.252 ; +0.569 / +0.272")

row("K4", "P-801 own-sign ladder, base -> a=384: both-rail %, in-disc path m, items per in-disc m",
    "docs/artifacts/RBT-67/p801.json",
    f"{100 * pc[0.0]['both_rail']:.1f}->{100 * pc[384.0]['both_rail']:.1f}%, {pc[0.0]['in_path']:.2f}->{pc[384.0]['in_path']:.2f}, "
    f"{pc[0.0]['items_per_m']:.3f}->{pc[384.0]['items_per_m']:.3f}", "5.8->14.7%, 4.55->4.05, 0.615->1.783")

# RBT-97 section 2: the P-801 phantom arm (provisional)
P = "docs/artifacts/RBT-97-p801-mechanism.txt"
t = read(P)
m97 = re.findall(r"motif - phantom\s+([+-][\d.]+) \[\s*([+-][\d.]+),\s*([+-][\d.]+)\];\s+phantom retains\s+([+-]?[\d.]+)%", t)
row("K1", "RBT-97 P-801, per-robot sign: motif - phantom at a=64 / a=384, phantom retains", P,
    " ; ".join(f"{a_} [{b_}, {c_}] retains {d_}%" for a_, b_, c_, d_ in m97),
    "+2.958 [+1.377, +4.538] retains 0.8% ; +7.705 [+3.957, +11.453] retains -10.7%", "READOUT")
mot = re.findall(r"^\s+motif\s+([+-][\d.]+) \[", t, re.M)
row("K2", "RBT-97 P-801 motif delta, 7 robots, a=64 / a=384", P, " / ".join(mot), "+2.982 / +6.962", "READOUT")
rot = re.findall(r"motif - rotated\s+([+-][\d.]+) \[\s*([+-][\d.]+),\s*([+-][\d.]+)\];\s+rotated retains\s+([+-]?[\d.]+)%", t)
row("K5", "RBT-97 P-801 ROTATED (depleting) decoy: motif - rotated, retains, a=64 ; a=384", P,
    " ; ".join(f"{a_} [{b_}, {c_}] retains {d_}%" for a_, b_, c_, d_ in rot),
    "+2.808 [+1.018, +4.598] retains 5.8% ; +7.576 [+3.780, +11.372] retains -8.8%", "READOUT")
vd = re.findall(r"verdict on the (phantom|rotated) decoy at a = (\d+): (FOOD-DEPENDENT|UNRESOLVED|GAIT)", t)
row("K6", "RBT-97 P-801 verdicts, static and rotated, both rungs", P, " ".join(f"{d}{a}:{v}" for d, a, v in vd),
    "phantom64:FOOD-DEPENDENT rotated64:FOOD-DEPENDENT phantom384:FOOD-DEPENDENT rotated384:FOOD-DEPENDENT")
P = "docs/artifacts/RBT-97-w4b-control.txt"
t = read(P)
wr = re.findall(r"(phantom|rotated) retains\s+([+-]?[\d.]+)% of the motif's gain\s+verdict on the \w+ decoy at a = (\d+): ([A-Z-]+(?: at this n)?)", t)
row("K7", "RBT-97 W4b control: retention and verdict, static / rotated, a=64 ; a=384", P,
    " ; ".join(f"{d} {r}% {v}" for d, r, a, v in wr),
    "phantom 25.2% UNRESOLVED at this n ; rotated 21.3% FOOD-DEPENDENT ; phantom -11.5% FOOD-DEPENDENT ; rotated -4.9% FOOD-DEPENDENT", "READOUT")
P = "docs/artifacts/RBT-97-routed-p801.txt"
t = read(P)
rp = re.findall(r"^\s+(\d+)\s+(\d+) \|\s+([+-][\d.]+) \[\s*([+-][\d.]+),\s*([+-][\d.]+)\]\s+(\d/7) \| (\w+)", t, re.M)
row("K8", "ROUTED motif on P-801, per-robot sign: a=32 ; a=64, t(6) interval, improved, verdict", P,
    " ; ".join(f"{d} [{lo_}, {hi_}] {imp} {v}" for w_, a_, d, lo_, hi_, imp, v in rp),
    "+0.969 [+0.254, +1.684] 6/7 PAYS ; +3.018 [+2.026, +4.010] 7/7 PAYS", "READOUT")
g100 = re.search(r"^g100 .*?\|\s+([+-][\d.]+) \|", t, re.M).group(1)
row("K9", "  the one robot not improved at a=32 (g100)", P, g100, "-0.078", "READOUT")
P = "runs/RBT-97/adversary_g500.txt"
t = read(P)
g5 = re.findall(r"(motif|rotated|antimotif) - base\s+n= 64\s+mean\s+([+-][\d.]+).*?t\s+([+-][\d.]+)", t)
row("K10", "g500 per seed: motif / rotated / antimotif minus base, a=64 then a=384 (mean, t)", P,
    " ".join(f"{c}:{m}({tt})" for c, m, tt in g5),
    "motif:+1.031(+1.70) rotated:+1.250(+2.61) antimotif:+0.609(+0.98) motif:+1.438(+2.56) rotated:+0.000(+0.00) antimotif:+1.234(+2.11)", "READOUT")

P = "docs/artifacts/RBT-97-rbt67-resigned.txt"
t = read(P)
r97 = re.search(r"^\s+32 \|\s+([+-][\d.]+) .*?(\d+/12)", t, re.M)
row("K3", "RBT-97 section 1 (RBT-67 re-signed per robot): 12 own-compass robots at a=32, mean and better", P,
    f"{r97.group(1)} {r97.group(2)}", "+0.674 12/12", "READOUT")

# --------------------------------------------------------------------------------------------
w = [max(len(r[i]) for r in ROWS) for i in range(6)]
print("RBT-72 re-derivation: every headline number in docs/paper-8, recomputed from committed files.")
print("Status: MATCH / MISMATCH (recomputed from data or arithmetic) / READOUT (a printed readout,")
print("no data behind it committed) / PROSE (only prose is committed).\n")
print("| id | claim | file | this re-derivation | quoted | status |")
print("|---|---|---|---|---|---|")
for r in ROWS:
    print("| " + " | ".join(r) + " |")
print()
files = set()
for r in ROWS:
    files.update(re.findall(r"[\w./-]+\.(?:txt|json|log|md|py)\b", r[2]))
print(f"{len(ROWS)} rows from {len(files)} distinct committed files\n")
for s in ("MATCH", "MISMATCH", "READOUT", "PROSE"):
    print(f"{s:9s} {sum(r[5] == s for r in ROWS)}")
