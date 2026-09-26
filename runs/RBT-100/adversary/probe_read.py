"""RBT-100 adversary probe P1 readout: what a C3 shift does to an established population, season by season.

    python runs/RBT-100/adversary/probe_read.py [SEED] [T] > runs/RBT-100/adversary/probe_read.txt

Reads the bulk of runs/RBT-100/data/probe-{plain,shift}-SEED/ (lineage.jsonl, history.json), made by
probe_run.sh.  Seed 901 is outside RBT-92's ten and T = 100 is not a registered onset: this probes the
design's mechanism claims (PREREGISTRATION.md sections 3.3, 3.4 and 4), not the C3 arms' class.

Prints, per fauna:
  1. the energy buffer at T - 1: mean and quartiles of stored energy over the living (section 3.3 assumes
     "at most a little above the birth threshold of 3");
  2. gross food and work charge per individual-season, [T-20, T) against [T, T+20) and [T+40, T+60),
     plain and shift (section 4 assumes gross halves and work does not move);
  3. deaths by cause and cohort in [T, T+60): starved (energy <= 0, age < 60) or aged out, and whether the
     dead were born before or after T;
  4. the NULL lines exactly as runs/RBT-100/readout.py computes them (k by RBT-89 section 8, excess deaths,
     births deficit, alive deficit, the UNDERSIZED test at n = 1);
  5. alive, births, deaths and mean_lifetime_score every 5 seasons from T - 5 to T + 60, plain and shift.
"""
import json
import statistics as st
import sys

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 901
T = int(sys.argv[2]) if len(sys.argv) > 2 else 100
KINDS = ("holistic", "conventional")
WORK_COST = 0.03  # per kJ; lineage work is in J


def load(arm):
    d = f"runs/RBT-100/data/probe-{arm}-{SEED}"
    rows = [json.loads(l) for l in open(f"{d}/lineage.jsonl")]
    hist = {(h["season"], h["population"]): h for h in json.load(open(f"{d}/history.json"))["history"]}
    return rows, hist


def q(v):
    v = sorted(v)
    return f"n {len(v):>3}  mean {st.fmean(v):6.2f}  q25 {v[len(v) // 4]:6.2f}  median {st.median(v):6.2f}  q75 {v[3 * len(v) // 4]:6.2f}" if v else "none"


def main():
    A = {a: load(a) for a in ("plain", "shift")}
    last = min(max(s for s, _ in h) for _, h in A.values())
    print(f"RBT-100 adversary probe P1: seed {SEED}, C3 shift (food-items=6) at T={T}; tables to season {last}")
    print()
    print("1. Stored energy over the living at the end of season T-1 (identical in both arms before T)")
    rows, _ = A["plain"]
    for k in KINDS:
        e = [r["energy"] for r in rows if r["population"] == k and r["generation"] == T - 1 and r["energy"] > 0 and r["age"] < 60]
        print(f"  {k:12s} {q(e)}")
    print()
    print("2. Per individual-season: gross food (items) and work charge (0.03/kJ); [T-20,T), [T,T+20), [T+40,T+60)")
    for k in KINDS:
        for a in ("plain", "shift"):
            rows, _ = A[a]
            cells = []
            for lo, hi in ((T - 20, T), (T, T + 20), (T + 40, T + 60)):
                rr = [r for r in rows if r["population"] == k and lo <= r["generation"] < hi and "food" in r and not r["exploded"]]
                if rr:
                    f = st.fmean(r["food"] for r in rr)
                    w = st.fmean(WORK_COST * r["work"] / 1000 for r in rr)
                    cells.append(f"[{lo - T:+d},{hi - T:+d}) food {f:5.3f} work {w:5.3f} net {f - w:+6.3f}")
                else:
                    cells.append(f"[{lo - T:+d},{hi - T:+d}) --")
            print(f"  {k:12s} {a:5s}  " + "   ".join(cells))
    print()
    print("3. Deaths in [T, T+60) by cause and by birth before/after T (last lineage row of each individual)")
    for a in ("plain", "shift"):
        rows, _ = A[a]
        lastrow, born = {}, {}
        for r in rows:
            key = (r["population"], r["name"])
            lastrow[key] = r
            born.setdefault(key, r["generation"] - r["age"] + 1 if r["age"] else r["generation"])
        for k in KINDS:
            c = {"starved, born<T": 0, "starved, born>=T": 0, "aged, born<T": 0, "aged, born>=T": 0}
            for (kk, n), r in lastrow.items():
                if kk != k or not (T <= r["generation"] < min(T + 60, last)):
                    continue
                cause = "aged" if r["age"] >= 60 else ("starved" if r["energy"] <= 0 else None)
                if cause is None:
                    continue
                c[f"{cause}, born{'<T' if born[(kk, n)] < T else '>=T'}"] += 1
            print(f"  {k:12s} {a:5s}  " + "  ".join(f"{x} {y:>3}" for x, y in c.items()))
    print()
    print("4. NULL lines as runs/RBT-100/readout.py computes them (n = 1)")
    hp, hs = A["plain"][1], A["shift"][1]
    g = lambda h, s, k, f: h.get((s, k), {}).get(f, 0)
    for k in KINDS:
        kk = max(0, sum(g(hs, t, k, "deaths") - g(hp, t, k, "deaths") for t in range(T, T + 10)))
        ex = [sum(g(hs, t, k, "deaths") - g(hp, t, k, "deaths") for t in range(T, T + w)) for w in (10, 30, 60) if T + w <= last + 1]
        bd = sum(g(hp, t, k, "births") - g(hs, t, k, "births") for t in range(T, min(T + 60, last + 1)))
        ad = [g(hp, T + w, k, "alive") - g(hs, T + w, k, "alive") for w in (10, 30, 60) if T + w <= last]
        und = len(ad) > 1 and ad[1] > 2 * kk + 2
        print(f"  {k:12s} k {kk:>3}  excess deaths [T,+10) [T,+30) [T,+60) {ex}  births deficit {bd:>4}  alive deficit T+10,+30,+60 {ad}"
              f"  -> {'UNDERSIZED' if und else 'not undersized'} by the pre-registered test")
    print()
    print("5. Every 5 seasons: alive / births / deaths / mean_lifetime_score / stored energy per head, plain | shift")
    for k in KINDS:
        print(f"  {k}")
        for s in range(T - 5, min(T + 61, last + 1), 5):
            cell = []
            for h in (hp, hs):
                e = h.get((s, k))
                cell.append("--" if not e else f"{e['alive']:>2} {e['births']:>2} {e['deaths']:>2} {e['mean_lifetime_score']:+.3f} E/head {e['total_energy'] / max(1, e['alive']):5.1f}")
            print(f"    {s - T:+4d}  {cell[0]}  |  {cell[1]}")


if __name__ == "__main__":
    main()
