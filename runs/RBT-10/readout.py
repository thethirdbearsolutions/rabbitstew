"""RBT-10 ecology readout.  usage: python runs/RBT-10/readout.py RUN_DIR [RUN_DIR ...]

Per run: alive / births / deaths / mean lifetime gain per population at the ticket's seasons, the
bottleneck (minimum alive, season) and recovery season (first back at capacity after it), the first
season the holistic mean gain exceeds the wheeled, extinctions, founders at the last season, and the
parent-child Pearson r of lifetime mean yield (last lineage record, evals >= 5 for child and parents)."""
import json, os, sys
import numpy as np
from rabbitstew.analysis import read_lineage, founders

SEASONS = [0, 11, 20, 32, 60, 100, 200, 300, 400, 500, 599]
KINDS = ("holistic", "conventional")
LABEL = {"holistic": "hol", "conventional": "wheel"}


def heritability(lin, kind, min_evals=5):
    recs = {name: r for (k, name), r in lin.items() if k == kind}
    xs, ys = [], []
    for r in recs.values():
        if r["evals"] < min_evals or not r["parents"]:
            continue
        ps = [recs[p]["fitness"] for p in r["parents"] if p in recs and recs[p]["evals"] >= min_evals]
        if len(ps) != len(r["parents"]):
            continue
        xs.append(float(np.mean(ps))); ys.append(r["fitness"])
    if len(xs) < 3:
        return float("nan"), len(xs)
    return float(np.corrcoef(xs, ys)[0, 1]), len(xs)


def readout(run):
    data = json.load(open(os.path.join(run, "history.json")))
    cap = json.load(open(os.path.join(run, "config.json"))).get("ecology", {}).get("capacity", 60)
    by = {k: {} for k in KINDS}
    for e in data["history"]:
        by[e["population"]][e["season"]] = e
    last = max(e["season"] for e in data["history"])
    name = os.path.basename(run.rstrip("/"))
    lines = [f"### {name}  (seasons completed: {last + 1})", ""]
    lines.append("| season | hol alive | hol births | hol deaths | hol mean gain | wheel alive | wheel births | wheel deaths | wheel mean gain |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for s in SEASONS:
        cells = []
        for k in KINDS:
            e = by[k].get(s)
            cells += [str(e["alive"]), str(e["births"]), str(e["deaths"]), f"{e['mean_lifetime_score']:+.2f}"] if e else ["-"] * 4
        lines.append(f"| {s} | " + " | ".join(cells) + " |")
    lines.append("")
    for k in KINDS:
        rows = sorted(by[k].items())
        alive = [(e["alive"], s) for s, e in rows]
        mn, ms = min(alive)
        rec = next((s for s, e in rows if s > ms and e["alive"] >= cap), None)
        ext = next((s for s, e in rows if e["alive"] == 0), None)
        if mn >= cap:
            lines.append(f"- **{LABEL[k]}** no bottleneck: never below capacity {cap}")
        else:
            lines.append(f"- **{LABEL[k]}** bottleneck: {mn} alive at season {ms}; recovery to {cap}: "
                         f"{'season ' + str(rec) if rec is not None else 'never'}"
                         + (f"; **extinct at season {ext}**" if ext is not None else ""))
    both = [s for s in sorted(by["holistic"]) if s in by["conventional"]]
    ahead = [s for s in both if by["holistic"][s]["mean_lifetime_score"] > by["conventional"][s]["mean_lifetime_score"]]
    first = ahead[0] if ahead else None
    sustained = None
    for s in both:
        window = [t for t in range(s, s + 10) if t in by["holistic"]]
        if len(window) == 10 and all(by["holistic"][t]["mean_lifetime_score"] > by["conventional"][t]["mean_lifetime_score"] for t in window):
            sustained = s; break
    lines.append(f"- **crossover** (holistic mean gain > wheeled): first at season {first if first is not None else 'never'}; "
                 f"first sustained for 10 seasons: {sustained if sustained is not None else 'never'}; "
                 f"holistic ahead in {len(ahead)} of {len(both)} seasons")
    for k in KINDS:
        e = by[k].get(last)
        if e:
            lines.append(f"- **{LABEL[k]} final** (season {last}): alive {e['alive']}, mean gain {e['mean_lifetime_score']:+.2f}, best lifetime {e['best_lifetime_score']:.2f}")
    log = run.rstrip("/") + ".log"
    if os.path.exists(log):
        died = [l.strip() for l in open(log) if "everyone died" in l]
        lines.append(f"- log: {len(died)} 'everyone died' line(s)" + ("; " + "; ".join(died[:3]) if died else ""))
    lin = read_lineage(run)
    for k in KINDS:
        recs = [r for (kk, _), r in lin.items() if kk == k]
        if not recs:
            continue
        lastg = max(r["generation"] for r in recs)
        f = founders(lin, k, [r["name"] for r in recs if r["generation"] == lastg])
        r, n = heritability(lin, k)
        lines.append(f"- **{LABEL[k]}** founders at season {lastg}: {f['founders']} of {f['of']} alive; yield heritability r = {r:.2f} (n = {n} parent-child pairs)")
    return "\n".join(lines)


if __name__ == "__main__":
    print("\n\n".join(readout(r) for r in sys.argv[1:]))
