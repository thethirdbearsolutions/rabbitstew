"""Read the analysis toolkit's output for the RBT-74 arms: what the champions of both arms *are*,
measured alone from rest, so the bout score is not read on its own (RBT-71).

Per run and population: the final best (generation 249) and the mean over the analysed
generations of the final fifth (200, 205, ..., 245, 249), from analysis.json:
approach progress on flat ground (m, 15 s), whether it fell, steering successes of 3, terrain
success of 6, block push (m), actuator work per metre, parts, mass, xy extent, height, units,
links, connected fraction, driven and active effectors, essential units, and the run's
parent-offspring heritability of the bout score.  Then the pre-registered secondary: approach
and terrain of the final holistic bests, protected minus unprotected, paired by seed.

    python runs/RBT-74/toolkit.py [runs/RBT-74]

Reads analysis.json only.  No simulation.
"""
import json
import os
import statistics as st
import sys

SEEDS = (201, 202, 203, 204)


def row(ind):
    cap, mo, co, le = ind["capability"], ind["morphology"], ind["controller"], ind.get("lesions") or {}
    return dict(
        gen=ind["generation"], name=ind["name"],
        approach=cap["approach"]["progress"], fell=cap["approach"]["fell"], wpm=cap["approach"].get("work_per_metre"),
        steer=cap["steering"]["successes"], terrain=cap["terrain"]["success_rate"], push=cap["push"]["block_displacement"],
        parts=mo["parts"], mass=mo["mass"], extent=mo["extent_xy"], height=mo["height"], nodes=mo["nodes"], expressed=mo["expressed_nodes"],
        units=co["units"], links=co["links"], connected=co["connected_fraction"], driven=co["driven_effectors"], active=co["active_effectors"],
        essential=le.get("essential_units"), effective=le.get("effective_fraction"),
    )


def load(run):
    a = json.load(open(os.path.join(run, "analysis.json")))
    out = {}
    for kind in ("holistic", "conventional"):
        rows = [row(i) for i in a["individuals"] if i["population"] == kind]
        final = [r for r in rows if r["gen"] == 249]
        last_fifth = [r for r in rows if r["gen"] >= 200]
        out[kind] = dict(final=final[0] if final else None, fifth=last_fifth, herit=(a.get("heritability") or {}).get(kind, {}).get("heritability"))
    return out


def fmt(r):
    eff = "" if r["effective"] is None else f"{r['effective']:.2f}"
    return (f"{r['approach']:+6.2f} {'y' if r['fell'] else 'n'}  {r['steer']}/3  {r['terrain']:.2f}  {r['push']:5.2f}  {r['wpm'] if r['wpm'] is None else round(r['wpm']):>6}  "
            f"{r['parts']:3d} {r['mass']:5.2f} {r['extent']:5.2f} {r['height']:5.2f}  {r['units']:3d}/{r['links']:<3d} {r['connected']:.2f}  {r['driven']}/{r['active']}  {str(r['essential']):>4} {eff:>5}")


def main(root="runs/RBT-74"):
    runs = {}
    for seed in SEEDS:
        for arm in ("base", "prot"):
            d = os.path.join(root, f"{arm}-{seed}")
            if os.path.exists(os.path.join(d, "analysis.json")):
                runs[(arm, seed)] = load(d)
    hdr = "run       pop           gen   approach fell steer terrain  push   J/m   parts  mass  ext  height  units/links conn  drv/act  ess  eff   herit"
    print("Final best (generation 249), measured alone from rest:")
    print(hdr)
    for (arm, seed), r in sorted(runs.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        for kind in ("holistic", "conventional"):
            f = r[kind]["final"]
            if f:
                print(f"{arm}-{seed:<5} {kind:12}  {f['gen']:3d}  {fmt(f)}  {r[kind]['herit']:+.3f}")
    print("\nMean over the analysed generations of the final fifth (200..249, up to 11 bests per population):")
    print("run       pop           n   approach  fell%  steer  terrain  push   parts  mass   units  links  conn  driven  essential")
    for (arm, seed), r in sorted(runs.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        for kind in ("holistic", "conventional"):
            rs = r[kind]["fifth"]
            if rs:
                m = lambda k: st.mean(x[k] for x in rs if x[k] is not None)
                print(f"{arm}-{seed:<5} {kind:12} {len(rs):2d}   {m('approach'):+6.2f}   {100 * m('fell'):3.0f}   {m('steer'):.2f}   {m('terrain'):.2f}   {m('push'):5.2f}  {m('parts'):5.1f} {m('mass'):6.2f}  {m('units'):5.1f}  {m('links'):5.1f}  {m('connected'):.2f}  {m('driven'):5.2f}  {m('essential'):5.2f}")
    print("\nPaired, protected minus unprotected, holistic:")
    print("seed   approach(final)  terrain(final)  approach(fifth mean)  terrain(fifth mean)  heritability")
    out = []
    for seed in SEEDS:
        b, p = runs.get(("base", seed)), runs.get(("prot", seed))
        if b and p and b["holistic"]["final"] and p["holistic"]["final"]:
            bf, pf = b["holistic"]["final"], p["holistic"]["final"]
            bm = st.mean(x["approach"] for x in b["holistic"]["fifth"]); pm = st.mean(x["approach"] for x in p["holistic"]["fifth"])
            bt = st.mean(x["terrain"] for x in b["holistic"]["fifth"]); pt = st.mean(x["terrain"] for x in p["holistic"]["fifth"])
            d = dict(seed=seed, approach_final=pf["approach"] - bf["approach"], terrain_final=pf["terrain"] - bf["terrain"], approach_fifth=pm - bm, terrain_fifth=pt - bt, herit=(p["holistic"]["herit"] or 0) - (b["holistic"]["herit"] or 0))
            out.append(d)
            print(f"{seed}   {d['approach_final']:+15.2f}  {d['terrain_final']:+14.2f}  {d['approach_fifth']:+20.2f}  {d['terrain_fifth']:+19.2f}  {d['herit']:+12.3f}")
    json.dump({"runs": {f"{a}-{s}": r for (a, s), r in runs.items()}, "paired": out}, open(os.path.join(root, "toolkit.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-74")
