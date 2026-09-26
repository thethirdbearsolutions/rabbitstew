"""RBT-99 (C2): the C2 block printed after RBT-92's readout, from committed tables only.

RBT-92's readout.py reads C2's arms unchanged (runs/RBT-99/readout.sh).  This adds what C2 owes beside its
verdict (PREREGISTRATION.md Amendment 1, answering the adversary's F4-F7):

  PRICE      per seed, co-evolved and designed R-shift (recovery) beside the mechanical price 0.05 x kJ from
             runs/RBT-99/price.txt, and R-shift + price: the part of R-shift that is not arithmetic (F4)
  TURNOVER   per seed and fauna, deaths and births over the transient and the recovery window in the shift
             arm against the baseline, and their ratio; a fauna churning at capacity reads alive 60 and a
             survivor-conditioned income, which D's test cannot see (F6)
  NULL NOTE  k counts excess deaths over [T, T + 10) only; the shift arm's deaths after T + 10 are printed
             beside it, since the impulse null matches only that first part (F7)
  FRAMING    the C2 claim line and the falsifier in the owner's words (F5)

An extinct fauna earns 0 in every later season (the coordinator's 13:10 ruling on RBT-92, item 1).

    python runs/RBT-99/c2_block.py      (readout.sh runs it after readout.py)
"""
import csv
import math
import os
import statistics as st

KINDS = ("holistic", "conventional")
SEEDS = [int(s) for s in os.environ.get("RBT92_SEEDS", "801 804 805 806 807 1 2 3 4 7").split()]
BASE_DIR = os.environ.get("RBT92_BASE_DIR", "runs/RBT-90")
ARM_DIR = os.environ.get("RBT99_ARM_DIR", "runs/RBT-99")
ONSET = os.environ.get("RBT92_ONSET", "runs/RBT-92/onset.txt")
PRICE = os.environ.get("RBT99_PRICE", "runs/RBT-99/price.txt")
BEFORE, TRANS, RECOV, TAIL, RUN = (int(x) for x in os.environ.get("RBT92_WINDOWS", "100,60,100,40,20").split(","))


def table(path):
    x, alive, deaths, births = ({k: {} for k in KINDS} for _ in range(4))
    rows = list(csv.DictReader(open(os.path.join(path, "seasons.txt")), delimiter="\t"))
    last = max(int(r["season"]) for r in rows)
    for r in rows:
        s, k = int(r["season"]), r["population"]
        x[k][s], alive[k][s] = float(r["mean_lifetime_score"]), int(r["alive"])
        deaths[k][s], births[k][s] = int(r["deaths"]), int(r["births"])
    for k in KINDS:
        for s in range(last + 1):
            alive[k].setdefault(s, 0)
            deaths[k].setdefault(s, 0)
            births[k].setdefault(s, 0)
            if alive[k][s] == 0:
                x[k][s] = 0.0  # a dead population earns nothing
    return x, alive, deaths, births


def onsets():
    out = {}
    for line in open(ONSET):
        f = line.rstrip("\n").split("\t")
        if f[0].lstrip("-").isdigit() and len(f) > 1 and f[1].isdigit():
            out[int(f[0])] = int(f[1])
    return out


def prices():
    out = {}
    if os.path.exists(PRICE):
        for r in csv.DictReader((l for l in open(PRICE) if "\t" in l), delimiter="\t"):
            if r.get("seed", "").lstrip("-").isdigit():
                out[(int(r["seed"]), r["fauna"])] = float(r["price"])
    return out


def f3(v):
    return "  --  " if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:+.3f}"


def main():
    T_of, P = onsets(), prices()
    print()
    print("C2 BLOCK (runs/RBT-99/c2_block.py; PREREGISTRATION.md Amendment 1)")
    if not P:
        print(f"  no {PRICE}: the price column is empty (python runs/RBT-99/price.py BULKDIR before the arms end)")
    print("  PRICE: R-shift (recovery, shift - base) against 0.05 x pre-onset kJ; 'net' = R-shift + price, the part that is not arithmetic")
    net = {k: [] for k in KINDS}
    turn = []
    for seed in SEEDS:
        T = T_of.get(seed)
        sp, bp = os.path.join(ARM_DIR, f"shift-{seed}"), os.path.join(BASE_DIR, f"forage-{seed}")
        if T is None or not (os.path.exists(os.path.join(sp, "seasons.txt")) and os.path.exists(os.path.join(bp, "seasons.txt"))):
            print(f"  {seed}: not read (no onset or no committed shift/baseline table)")
            continue
        S, B = table(sp), table(bp)
        a, b = T + TRANS, T + TRANS + RECOV
        cells = []
        for k in KINDS:
            rs = st.fmean([S[0][k][s] - B[0][k][s] for s in range(a, b) if s in S[0][k] and s in B[0][k]] or [float("nan")])
            p = P.get((seed, k), float("nan"))
            net[k].append(rs + p)
            cells.append(f"{k} R-shift {f3(rs)} price {f3(-p)} net {f3(rs + p)}")
        print(f"  {seed}: " + ";  ".join(cells))
        for k in KINDS:
            for w, (lo, hi) in (("transient", (T, T + TRANS)), ("recovery", (a, b))):
                ds, db = sum(S[2][k].get(s, 0) for s in range(lo, hi)), sum(B[2][k].get(s, 0) for s in range(lo, hi))
                bs, bb = sum(S[3][k].get(s, 0) for s in range(lo, hi)), sum(B[3][k].get(s, 0) for s in range(lo, hi))
                ratio = ds / db if db else (float("inf") if ds else float("nan"))
                turn.append((seed, k, w, ds, db, bs, bb, ratio))
        late = sum(S[2]["conventional"].get(s, 0) for s in range(T + 10, T + TRANS))
        early = sum(S[2]["conventional"].get(s, 0) for s in range(T, T + 10))
        print(f"      null note: designed deaths in the shift arm over [T, T+10) {early} (k's window) and over [T+10, T+{TRANS}) {late}")
    for k in KINDS:
        v = [x for x in net[k] if not math.isnan(x)]
        if v:
            print(f"  mean net of the price, {k}: {st.fmean(v):+.4f} over {len(v)} seeds")
    print("  TURNOVER: deaths and births per window, shift arm against the baseline (ratio = deaths shift / deaths base)")
    for seed, k, w, ds, db, bs, bb, ratio in turn:
        flag = "   >= 2x base: any A or C sentence carries this number" if (k == "conventional" and not math.isnan(ratio) and ratio >= 2) else ""
        print(f"  {seed:>4} {k:12s} {w:9s}: deaths {ds:4d} vs {db:4d}  births {bs:4d} vs {bb:4d}  ratio {ratio:.2f}{flag}")
    print("  FRAMING (docs/held-out-challenges.md section 2, C2, and section 9), whatever the class above:")
    print("    Claim tested: survivorship of the co-evolved population at an economic boundary the designed body's budget is not")
    print("    expected to survive. That is a different claim from the owner's (it is about one body's cheapness, not two bodies'")
    print("    contest), and a C2 result is reported as such.")
    print("    Falsifier, in the owner's words: \"the designed body wins on the held-out challenge\" (class C above, and class E2,")
    print("    co-evolved bankrupt and designed not, as its strongest form; readout.py's strings quote RBT-92's wording, \"after")
    print("    the shift\", for the same classes).")
    print("    A co-evolved 'does not hold up' no larger than its price is the price, not maladaptation (forbidden reading (b)).")


if __name__ == "__main__":
    main()
