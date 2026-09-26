"""RBT-99 (C2, dearer work): will an EVOLVED population survive --work-cost 0.08?  Arithmetic on committed
data, no run.  Answers the ticket's item 3 (is class E, both faunas failing inside the transient, the likely
outcome?) and sets the prior for classes D and E.

The shift changes one term of a robot's season gain (rabbitstew/simulation.py, food_gain):

    gain = items eaten x 1  -  work_cost x kJ          (before the 0.25 basal cost; solvent above +0.25)

so going 0.03 -> 0.08 lowers every individual's gain by exactly 0.05 x its kJ that season and changes
nothing else.  Two committed sources, both on the dense foraging baseline economy (12 items, 0.03 per kJ,
basal 0.25, initial energy 3, breed at 3, pay 1; docs/held-out-challenges.md section 1):

  kJ a season:  RBT-10's solo probes of the per-season bests, seeds 802 and 803 at w = 0.03
                (runs/RBT-10/forage-w0.03-80x.probe.txt, eight fresh draws each, "intact" column),
                seasons 0 (founders) and 100, 300, 590 (evolved).  The only committed per-kJ figures for
                evolved individuals of this economy; they are bests, not population means.
  income:       RBT-71's population mean_lifetime_score, seeds 804-806, seasons 100-599
                (runs/RBT-71/forage-80x/seasons.txt): this economy, the same axis the readout scores.

    python runs/RBT-99/work_budget.py > runs/RBT-99/work_budget.txt
"""
import csv
import re
import statistics

EXTRA = 0.08 - 0.03
BASAL = 0.25
PAT = re.compile(r"^(holistic|conventional)\s+g\s*(\d+)")
INTACT = re.compile(r"intact: food ([\d.]+) disp [\d.]+ path [\d.]+ work ([\d.]+)kJ")


def probes(path):
    out, cur = [], None
    for line in open(path):
        m = PAT.match(line)
        if m:
            cur = (m.group(1), int(m.group(2)))
            continue
        m = INTACT.search(line)
        if m and cur:
            out.append((cur[0], cur[1], float(m.group(1)), float(m.group(2))))
            cur = None
    return out


def main():
    print(__doc__.split("\n\n")[0])
    print()
    print("1. kJ a season of the probed bests (RBT-10, w = 0.03), and what 0.08 adds")
    print(f"{'seed':>5} {'fauna':12} {'season':>6} {'items':>6} {'kJ':>6} {'charge@0.03':>11} {'charge@0.08':>11} {'added':>7} {'items/kJ':>9} {'break-even w':>12}")
    kj = {("holistic", True): [], ("conventional", True): [], ("holistic", False): [], ("conventional", False): []}
    for seed in (802, 803):
        for fauna, g, items, w in probes(f"runs/RBT-10/forage-w0.03-{seed}.probe.txt"):
            kj[(fauna, g > 0)].append(w)
            be = (items - BASAL) / w * 1000 if w else float("inf")  # w per kJ at which items - w*kJ = basal
            print(f"{seed:>5} {fauna:12} {g:>6} {items:6.2f} {w:6.1f} {0.03 * w:11.3f} {0.08 * w:11.3f} {EXTRA * w:7.3f} {items / w:9.3f} {be / 1000:12.3f}")
    print()
    for fauna in ("holistic", "conventional"):
        v = sorted(kj[(fauna, True)])
        print(f"  evolved {fauna:12} bests (seasons 100-590, n={len(v)}): kJ {v[0]:.1f}..{v[-1]:.1f}, median {statistics.median(v):.2f};"
              f" added charge at 0.08: {EXTRA * v[0]:.3f}..{EXTRA * v[-1]:.3f}, median {EXTRA * statistics.median(v):.3f}")
    print()
    print("2. population income, seasons 100-599 (RBT-71, this economy), and the same less the added charge")
    print("   (arithmetic: the evolved bests' kJ range applied to the population mean; the arm measures the real one)")
    lo_hi = {f: (EXTRA * min(kj[(f, True)]), EXTRA * max(kj[(f, True)]), EXTRA * statistics.median(kj[(f, True)])) for f in ("holistic", "conventional")}
    print(f"{'seed':>5} {'fauna':12} {'mean income':>11} {'min 100-season window':>22} {'at 0.08, median kJ':>19} {'at 0.08, range':>16} {'vs basal 0.25':>14}")
    for seed in (804, 805, 806):
        rows = list(csv.DictReader(open(f"runs/RBT-71/forage-{seed}/seasons.txt"), delimiter="\t"))
        for fauna in ("holistic", "conventional"):
            x = {int(r["season"]): float(r["mean_lifetime_score"]) for r in rows if r["population"] == fauna}
            v = [x[s] for s in range(100, 600) if s in x]
            m = statistics.mean(v)
            wins = min(statistics.mean([x[s] for s in range(a, a + 100) if s in x]) for a in range(100, 501))
            lo, hi, med = lo_hi[fauna]
            verdict = "above" if m - hi > BASAL else ("BELOW" if m - lo < BASAL else "straddles")
            print(f"{seed:>5} {fauna:12} {m:11.3f} {wins:22.3f} {m - med:19.3f} {m - hi:7.3f}..{m - lo:7.3f} {verdict:>14}")
    print()
    print("3. reading (arithmetic on the rows above, not a measurement)")
    print("  - the designed fauna: every evolved best spends 17-27 kJ, so 0.08 takes 0.86-1.35 a season more from")
    print("    a population whose mean income is +0.85 to +0.90; every row lands below the basal cost: class D's")
    print("    income and capacity triggers are expected in the transient on most seeds unless selection finds a")
    print("    Pioneer brain far cheaper than any probed (intact Pioneer bests on record: 12.7 kJ at the least, RBT-13")
    print("    g100, another economy; 15.0 kJ for RBT-21's economy-selected c0-4) within about two reproduction events.")
    print("  - the co-evolved fauna: evolved bests spend 2.3-7.8 kJ, so 0.08 takes 0.12-0.39 a season more from a")
    print("    population whose mean income is +0.94 to +1.06; every row stays above the basal cost, the worst by")
    print("    0.30 (806 at the top of the range). Class E needs co-evolved income below 0.25 on 8/10 seeds (or both extinct): it is")
    print("    not the likely outcome at 0.08. RBT-21's extinction was of founders (73% of lumps ate nothing,")
    print("    newborns of non-eaters); an evolved population's newborns inherit an eating, cheap body.")


if __name__ == "__main__":
    main()
