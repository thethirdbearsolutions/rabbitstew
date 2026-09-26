"""RBT-92: the natural cohort cycle, measured from committed data (no run).

Reads seasons.txt and lineage-last.txt of the six committed 600-season ecology runs on the
dense foraging baseline config (runs/RBT-71/forage-80x: selected, the RBT-90/RBT-92 economy;
runs/RBT-71/neutral-80x: the no-starvation drift control, where turnover is by max_age alone,
the ecology analogue of RBT-80's drift arms). Pre-RBT-95 runs: they are read as recorded, never
regenerated from their seeds.

Per run and population it prints:
  * peaks: every 10-season window [s, s+10) with s >= 100 whose deaths reach 20 (RBT-89 §8's
    threshold: a third of capacity), merged into runs of consecutive window starts;
  * the largest 10-season deaths sum after season 100, and where;
  * mean age per season, reconstructed from lineage-last.txt (an individual observed last at
    season g with age a is alive over [g - a, g]; the reconstruction's alive count is asserted
    equal to seasons.txt's alive in every season and population, so the ages are a derivation,
    not a guess), and the largest 10-season fall in mean age after season 100;
  * the lag-60 autocorrelation of per-season deaths over seasons 100..599 against the median
    |autocorrelation| at lags 40..80 excluding 55..65 (a synchronised cohort under max_age = 60
    would show as a lag-60 peak);
  * the period: the lag in 30..90 at which that autocorrelation is largest;
  * deaths in the candidate onset window [400, 410) and in the protocol's stagger seasons
    (RBT-89 §8: 371, 431, 491, 551) +-5.

  python runs/RBT-92/cohort_cycle.py > runs/RBT-92/cohort_cycle.txt
"""
import csv
import os
import statistics
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "RBT-71")
RUNS = [f"{kind}-{seed}" for kind in ("forage", "neutral") for seed in (804, 805, 806)]
POPS = ("holistic", "conventional")
PEAK = 20
WIN = 10
START = 100
STAGGER = (371, 431, 491, 551)


def read(run):
    d = os.path.join(ROOT, run)
    seasons = list(csv.DictReader(open(os.path.join(d, "seasons.txt")), delimiter="\t"))
    rows = list(csv.DictReader(open(os.path.join(d, "lineage-last.txt")), delimiter="\t"))
    return seasons, rows


def acf(x, lag):
    m = statistics.fmean(x)
    v = sum((a - m) ** 2 for a in x)
    return sum((x[i] - m) * (x[i + lag] - m) for i in range(len(x) - lag)) / v if v else 0.0


def main():
    print(__doc__.split("\n\n")[0])
    print()
    summary = []
    for run in RUNS:
        seasons, rows = read(run)
        n = 1 + max(int(r["season"]) for r in seasons)
        for pop in POPS:
            S = {int(r["season"]): r for r in seasons if r["population"] == pop}
            deaths = [int(S[s]["deaths"]) if s in S else 0 for s in range(n)]
            alive = [int(S[s]["alive"]) if s in S else 0 for s in range(n)]
            cnt = [0] * n
            agesum = [0] * n
            for r in rows:
                if r["population"] != pop:
                    continue
                g, a = int(r["generation"]), int(r["age"])
                for s in range(max(g - a, 0), g + 1):
                    cnt[s] += 1
                    agesum[s] += a - (g - s)
            bad = [s for s in range(n) if cnt[s] != alive[s]]
            assert not bad, f"{run} {pop}: lineage-last alive != seasons.txt alive at {bad[:5]}"
            mage = [agesum[s] / cnt[s] if cnt[s] else float("nan") for s in range(n)]
            win = {s: sum(deaths[s:s + WIN]) for s in range(START, n - WIN + 1)}
            hot = [s for s in sorted(win) if win[s] >= PEAK]
            groups = []
            for s in hot:
                if groups and s == groups[-1][1] + 1:
                    groups[-1][1] = s
                else:
                    groups.append([s, s])
            smax = max(win, key=lambda s: (win[s], -s))
            fall = {s: mage[s] - mage[s + WIN] for s in range(START, n - WIN)}
            fmax = max(fall, key=lambda s: (fall[s], -s))
            x = deaths[START:n]
            a60 = acf(x, 60)
            ref = statistics.median(abs(acf(x, L)) for L in range(40, 81) if not 55 <= L <= 65)
            period = max(range(30, 91), key=lambda L: acf(x, L))
            d400 = sum(deaths[400:410])
            stag = {t: sum(deaths[t - 5:t + 5]) for t in STAGGER}
            peaks = ", ".join(f"[{a},{b + WIN})max{max(win[s] for s in range(a, b + 1))}" for a, b in groups) or "none"
            print(f"{run:12s} {pop:12s} peaks>={PEAK}/60 after {START}: {peaks}")
            print(f"{'':25s} max 10-season deaths after {START}: {win[smax]}/60 at [{smax},{smax + WIN}); "
                  f"mean age {min(mage[START:]):.1f}..{max(mage[START:]):.1f}, largest 10-season fall "
                  f"{fall[fmax]:.1f} at {fmax}->{fmax + WIN} ({mage[fmax]:.1f}->{mage[fmax + WIN]:.1f})")
            print(f"{'':25s} deaths acf lag60 {a60:+.3f} vs median |acf| lags 40-80 {ref:.3f}; "
                  f"deaths [400,410) {d400}/60; stagger +-5: " + ", ".join(f"{t}:{v}" for t, v in stag.items()))
            summary.append((run, pop, len(groups), win[smax], smax, fall[fmax], a60, d400, max(
                (win[s] for s in range(380, 400)), default=0), max(win[s] for s in range(400, 591)), period))
    print()
    print("summary: run population | peak groups after 100 | max 10-season deaths (start) | largest "
          "10-season mean-age fall | acf60 | period | deaths[400,410) | max window starting 380..399 | max window starting 400..590")
    for r in summary:
        print(f"  {r[0]:12s} {r[1]:12s} | {r[2]} | {r[3]:2d}/60 ({r[4]}) | {r[5]:5.1f} | {r[6]:+.3f} | {r[10]} | {r[7]:2d}/60 | {r[8]:2d}/60 | {r[9]:2d}/60")
    sel = [r for r in summary if r[0].startswith("forage")]
    print()
    print(f"selected arms (forage-80x), both populations: {sum(1 for r in sel if r[2] == 0)}/{len(sel)} "
          f"population-runs with no 10-season deaths window >= {PEAK}/60 after season {START}; "
          f"max 10-season deaths after {START} over all {len(sel)}: {max(r[3] for r in sel)}/60")
    drift = [r for r in summary if r[0].startswith("neutral")]
    print(f"drift arms (neutral-80x): {sum(1 for r in drift if r[2] > 0)}/{len(drift)} population-runs with "
          f"a window >= {PEAK}/60 after {START}; max {max(r[3] for r in drift)}/60")


if __name__ == "__main__":
    sys.exit(main())
