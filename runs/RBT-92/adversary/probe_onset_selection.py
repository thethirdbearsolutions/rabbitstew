"""RBT-92 adversary probe A: does the trough rule select on the control's own post-onset outcome?

onset.py picks T in [340, 400] minimising D(T) = deaths of both faunas over [T-10, T+10) of the
FINISHED baseline.  Half that window, [T, T+10), is after the onset: it is the control arm's
outcome, and it is exactly the window cull_k.py subtracts from the shift arm's deaths to size the
null.  Deaths in [T, T+10) split into
  * age-outs (an individual reaching max_age = 60): fixed by the age structure at T-1, the same in
    every arm (shared prefix), so selecting on them is selecting on pre-onset state; and
  * starvation deaths: the control's post-onset luck, not shared by the shift arm.
The probe decomposes, on RBT-71's committed forage runs (the RBT-92 economy; the same files
cohort_cycle.py reads; no run, no income column read), the deaths in [T, T+10) at the rule's T
against the same quantity averaged over every candidate T in [340, 400], and does the same for a
rule that reads only pre-onset state (deaths [T-10, T) plus the age-outs due in [T, T+10), which
the age structure at T-1 fixes).

    python runs/RBT-92/adversary/probe_onset_selection.py > runs/RBT-92/adversary/probe_onset_selection.txt
"""
import csv
import os
import statistics

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "RBT-71")
RUNS = [f"forage-{s}" for s in (804, 805, 806)]
KINDS = ("holistic", "conventional")
LO, HI, HALF, MAXAGE = 340, 400, 10, 60


def load(run):
    d = os.path.join(ROOT, run)
    seasons = list(csv.DictReader(open(os.path.join(d, "seasons.txt")), delimiter="\t"))
    rows = list(csv.DictReader(open(os.path.join(d, "lineage-last.txt")), delimiter="\t"))
    last = max(int(r["season"]) for r in seasons)
    deaths = {(int(r["season"]), r["population"]): int(r["deaths"]) for r in seasons}
    age_out, starve = {}, {}
    for r in rows:
        g, a = int(r["generation"]), int(r["age"])
        if g >= last:  # alive at the end
            continue
        # measured: a death counted in season s is the individual's last lineage row at generation s - 1,
        # and an age-out is last observed at age max_age - 1 (1052 of the 1.4k rows at 804 read age 59)
        key = (g + 1, r["population"])
        m = age_out if a >= MAXAGE - 1 else starve
        m[key] = m.get(key, 0) + 1
    # the decomposition must add up to the table's deaths
    bad = [k for k, v in deaths.items() if 0 < k[0] < last and v != age_out.get(k, 0) + starve.get(k, 0)]
    return deaths, age_out, starve, bad


def tot(m, a, b):
    return sum(m.get((s, k), 0) for s in range(a, b) for k in KINDS)


def main():
    print(__doc__.split("\n\n")[0])
    print()
    print("run         rule        T   D(T)  post[T,T+10): all  age-out  starve | mean over T in [340,400]: all  age-out  starve")
    summ = []
    for run in RUNS:
        deaths, ao, st, bad = load(run)
        inwin = [k for k in bad if LO - HALF <= k[0] < HI + HALF]
        print(f"{run}: decomposition age-out + starvation = seasons.txt deaths on {len(deaths) - len(bad)}/{len(deaths)} (season, fauna) cells; "
              f"mismatches inside [{LO - HALF}, {HI + HALF}): {len(inwin)}")
        D = {T: tot(deaths, T - HALF, T + HALF) for T in range(LO, HI + 1)}
        Tr = min(D, key=lambda t: (D[t], -t))
        Dp = {T: tot(deaths, T - HALF, T) + tot(ao, T, T + HALF) for T in range(LO, HI + 1)}
        Tp = min(Dp, key=lambda t: (Dp[t], -t))
        ma = statistics.fmean(tot(deaths, T, T + HALF) for T in D)
        mo = statistics.fmean(tot(ao, T, T + HALF) for T in D)
        ms = statistics.fmean(tot(st, T, T + HALF) for T in D)
        for name, T, dv in (("trough", Tr, D[Tr]), ("pre-T only", Tp, Dp[Tp])):
            print(f"{run:11s} {name:10s} {T:4d} {dv:5d}  {tot(deaths, T, T + HALF):17d}  {tot(ao, T, T + HALF):7d}  {tot(st, T, T + HALF):6d} | "
                  f"{ma:30.1f}  {mo:7.1f}  {ms:6.1f}")
            summ.append((run, name, tot(st, T, T + HALF), ms))
        # how much of D's variation over the candidate range is starvation (post-onset luck)?
        sd_ao = statistics.pstdev(tot(ao, T, T + HALF) for T in D)
        sd_st = statistics.pstdev(tot(st, T, T + HALF) for T in D)
        print(f"{'':11s} over T in [340,400]: SD of post-onset age-outs {sd_ao:.1f}, of post-onset starvation deaths {sd_st:.1f}")
    print()
    for name in ("trough", "pre-T only"):
        v = [(a - m) for r, n, a, m in summ if n == name]
        print(f"{name:10s}: starvation deaths in [T, T+10) minus their mean over candidate T, per run {['%+.1f' % x for x in v]}; mean {statistics.fmean(v):+.1f}")
    print("A negative figure is the control's post-onset luck that the rule selected; cull_k.py subtracts the control's")
    print("[T, T+10) deaths from the shift arm's, so k is inflated by about its size (both faunas together).")


if __name__ == "__main__":
    main()
