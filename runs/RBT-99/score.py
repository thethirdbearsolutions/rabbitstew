"""RBT-99 (C2): the pre-registered predictions scored, from committed files only.

Reads each seed's committed tables (runs/RBT-90/forage-SEED/seasons.txt as the base, runs/RBT-99/shift-SEED and
cull-SEED/seasons.txt), runs/RBT-99/cull-k-SEED.txt, runs/RBT-99/price.txt, runs/RBT-92/onset.txt, and the
committed readout (runs/RBT-99/readout.txt) for the lines readout.py computes itself (class, r, recovery,
carriage).  An extinct fauna earns 0 (the 13:10 ruling).  Windows as registered: transient [T, T+60), recovery
[T+60, T+160).  Prints each prediction with its registered probability and HIT / MISS; the amended predictions
(Amendments 1-2) are the scored set, the original section 10 is printed beside them.

    python runs/RBT-99/score.py > runs/RBT-99/score.txt
"""
import csv
import re
import statistics as st

SEEDS = [801, 804, 805, 806, 807, 1, 2, 3, 4, 7]
KINDS = ("holistic", "conventional")
BASAL, FLOOR = 0.25, 12


def table(path):
    x, alive, deaths = ({k: {} for k in KINDS} for _ in range(3))
    rows = list(csv.DictReader(open(f"{path}/seasons.txt"), delimiter="\t"))
    last = max(int(r["season"]) for r in rows)
    for r in rows:
        s, k = int(r["season"]), r["population"]
        x[k][s], alive[k][s], deaths[k][s] = float(r["mean_lifetime_score"]), int(r["alive"]), int(r["deaths"])
    for k in KINDS:
        for s in range(last + 1):
            alive[k].setdefault(s, 0)
            deaths[k].setdefault(s, 0)
            if alive[k][s] == 0:
                x[k][s] = 0.0
    return x, alive, deaths


def onsets():
    return {int(l.split("\t")[0]): int(l.split("\t")[1]) for l in open("runs/RBT-92/onset.txt") if l.split("\t")[0].isdigit()}


def cullk(seed):
    for l in open(f"runs/RBT-99/cull-k-{seed}.txt"):
        if l.startswith("cull\t"):
            return {p.split("=")[0]: int(p.split("=")[1]) for p in l.split("\t")[1].strip().split(",")}


def mean(v):
    return st.fmean(v) if v else float("nan")


T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}


def ci(v):
    m, sd = st.fmean(v), st.stdev(v)
    hw = T975[len(v) - 1] * sd / len(v) ** 0.5
    return f"{m:+.4f}  95% t({len(v) - 1}) [{m - hw:+.4f}, {m + hw:+.4f}]  sd {sd:.4f}  positive {sum(x > 0 for x in v)}/{len(v)}"


def net_share(per, mp):
    return mean([w["holistic"]["rshift_rc"] + w["holistic"]["price"] for w in per]) / mp


def main():
    print(__doc__.split("\n\n")[0])
    T_of = onsets()
    price = {(int(r["seed"]), r["fauna"]): float(r["price"])
             for r in csv.DictReader((l for l in open("runs/RBT-99/price.txt") if "\t" in l), delimiter="\t")}
    ro = open("runs/RBT-99/readout.txt").read()
    cls = re.search(r"CLASS: (.*)", ro).group(1)
    r = float(re.search(r"  r = ([0-9.]+) \(the larger\)", ro).group(1))
    per = []
    for seed in SEEDS:
        T = T_of[seed]
        B, S, C = table(f"runs/RBT-90/forage-{seed}"), table(f"runs/RBT-99/shift-{seed}"), None
        k = cullk(seed)
        if k != {"holistic": 0, "conventional": 0}:
            C = table(f"runs/RBT-99/cull-{seed}")
        tr, rc = range(T, T + 60), range(T + 60, T + 160)
        row = {"seed": seed, "T": T, "k": k}
        for f in KINDS:
            row[f] = {
                "inc_tr": mean([S[0][f][s] for s in tr]), "inc_rc": mean([S[0][f][s] for s in rc]),
                "min_tr": min(S[1][f][s] for s in tr), "min_rc": min(S[1][f][s] for s in rc),
                "extinct160": any(S[1][f][s] == 0 for s in range(T, T + 160)),
                "rshift_rc": mean([S[0][f][s] - B[0][f][s] for s in rc]),
                "rnull_rc": mean([S[0][f][s] - C[0][f][s] for s in rc]) if C else None,
                "dratio_tr": sum(S[2][f][s] for s in tr) / max(1, sum(B[2][f][s] for s in tr)),
                "price": price[(seed, f)],
            }
            g = row[f]
            g["bankrupt"] = g["inc_tr"] < BASAL or g["inc_rc"] < BASAL or min(g["min_tr"], g["min_rc"]) < FLOOR
        row["rbody_shift"] = mean([S[0]["holistic"][s] - S[0]["conventional"][s] for s in rc])
        row["rbody_base"] = mean([B[0]["holistic"][s] - B[0]["conventional"][s] for s in rc])
        row["alive_T1"] = {f: B[1][f][T - 1] for f in KINDS}
        per.append(row)

    print()
    print("PER SEED (shift arm; recovery window unless named)")
    print("  seed   T  des inc tr/rc   des min tr/rc  des bankrupt  des dratio tr  coev inc rc  coev R-shift  price  net   R-body shift/base  k hol/con (alive T-1)")
    for w in per:
        d, h = w["conventional"], w["holistic"]
        print(f"  {w['seed']:>4} {w['T']} {d['inc_tr']:+.3f}/{d['inc_rc']:+.3f}   {d['min_tr']:>3}/{d['min_rc']:<3}       {str(d['bankrupt']):5s}      "
              f"{d['dratio_tr']:5.2f}        {h['inc_rc']:+.3f}      {h['rshift_rc']:+.3f}     {h['price']:.3f} {h['rshift_rc'] + h['price']:+.3f}   "
              f"{w['rbody_shift']:+.3f}/{w['rbody_base']:+.3f}    {w['k']['holistic']}/{w['k']['conventional']} ({w['alive_T1']['conventional']})")
    n = len(per)
    des_b = sum(w["conventional"]["bankrupt"] for w in per)
    coev_b = sum(w["holistic"]["bankrupt"] for w in per)
    surv = [w for w in per if not w["conventional"]["extinct160"]]
    print()
    print(f"  designed bankrupt by D's test: {des_b}/{n}; co-evolved bankrupt: {coev_b}/{n}; class (readout.txt): {cls}; r {r:.4f}")
    print(f"  R-body recovery, seeds where the designed fauna never reached 0 before T+160 ({len(surv)}/{n}): "
          f"shift {mean([w['rbody_shift'] for w in surv]):+.4f}, base {mean([w['rbody_base'] for w in surv]):+.4f}, "
          f"shift - base {mean([w['rbody_shift'] - w['rbody_base'] for w in surv]):+.4f}")
    print("  intervals (per-seed values above; t(n-1) 95%):")
    print(f"    shift - base R-body, recovery, all seeds:       {ci([w['rbody_shift'] - w['rbody_base'] for w in per])}")
    print(f"    shift - base R-body, recovery, designed-surviving seeds: {ci([w['rbody_shift'] - w['rbody_base'] for w in surv])}")
    print(f"    co-evolved R-shift, designed-surviving seeds:   {ci([w['holistic']['rshift_rc'] for w in surv])}")
    print(f"    designed R-shift, designed-surviving seeds:     {ci([w['conventional']['rshift_rc'] for w in surv])}")
    print(f"    co-evolved net of the price (R-shift + price):  {ci([w['holistic']['rshift_rc'] + w['holistic']['price'] for w in per])}")
    mp = mean([w["holistic"]["price"] for w in per])
    print(f"    co-evolved mean price {mp:.4f}; mean net / mean price = {net_share(per, mp):.3f}")
    print(f"  R-body recovery, all seeds: shift {mean([w['rbody_shift'] for w in per]):+.4f}, base {mean([w['rbody_base'] for w in per]):+.4f}, "
          f"shift - base {mean([w['rbody_shift'] - w['rbody_base'] for w in per]):+.4f} (= co-evolved R-shift - designed R-shift)")

    def rec_list(fauna, arm):
        m = re.search(rf"paired \(primary\)\s+{fauna}\s+{arm}\s+: .*per seed (\[.*\])", ro)
        return eval(m.group(1))

    def lline(name):
        return float(re.search(rf"T\+160\s+L\s+{name}\s*: ([-+][0-9.]+)", ro).group(1))

    k1 = [w["k"]["holistic"] for w in per]
    k2 = [w["k"]["conventional"] for w in per]
    capped = sum(w["k"]["conventional"] >= w["alive_T1"]["conventional"] for w in per)
    kpos = [w for w in per if w["k"]["holistic"] > 0]
    rn = mean([w["holistic"]["rnull_rc"] for w in kpos])
    rs_k = mean([w["holistic"]["rshift_rc"] for w in kpos])
    rs_h = mean([w["holistic"]["rshift_rc"] for w in per])
    rs_c = mean([w["conventional"]["rshift_rc"] for w in per])
    net_h = mean([w["holistic"]["rshift_rc"] + w["holistic"]["price"] for w in per])
    fals_i = sum(w["conventional"]["inc_rc"] >= BASAL and w["conventional"]["min_rc"] >= FLOOR for w in per)
    fals_ii = sum(w["holistic"]["inc_rc"] < BASAL for w in per)
    hs = rec_list("holistic", "shift")
    cs = rec_list("conventional", "shift")
    hc = rec_list("holistic", "cull")

    def hit(b):
        return "HIT " if b else "MISS"

    print()
    print("SCORED (Amendments 1-2, the registered set; the original section 10 value in brackets)")
    rows = [
        ("class A", 0.12, cls.startswith("A"), "[orig 0.07]"),
        ("class D", 0.30, cls.startswith("D"), "[orig 0.75]"),
        ("class F (modal)", 0.33, cls.startswith("F"), "[orig 0.10]"),
        (f"designed D-half on >= 8/10 seeds: {des_b}/10", 0.35, des_b >= 8, "[orig 0.8]"),
        (f"designed alive < 12 in the transient on >= 7/10: {sum(w['conventional']['min_tr'] < 12 for w in per)}/10", 0.15,
         sum(w["conventional"]["min_tr"] < 12 for w in per) >= 7, "[orig 0.65]"),
        (f"designed extinct by T+160 on >= 5/10: {sum(w['conventional']['extinct160'] for w in per)}/10", 0.10,
         sum(w["conventional"]["extinct160"] for w in per) >= 5, "[orig 0.5]"),
        (f"designed transient deaths >= 2x base on >= 8/10: {sum(w['conventional']['dratio_tr'] >= 2 for w in per)}/10", 0.80,
         sum(w["conventional"]["dratio_tr"] >= 2 for w in per) >= 8, "[new in Amendment 1]"),
        (f"designed R-shift recovery -0.25 (-0.8..+0.3): {rs_c:+.4f}", None, -0.8 <= rs_c <= 0.3, "[orig -0.75]"),
        (f"co-evolved survives on 10/10 (alive >= 12, recovery income >= 0.25): {n - coev_b}/10", 0.85, coev_b == 0, "[orig 0.85]"),
        (f"co-evolved R-shift recovery -0.24 (-0.40..-0.10): {rs_h:+.4f}", None, -0.40 <= rs_h <= -0.10, "[orig -0.17]"),
        (f"co-evolved net of the price +0.03 (-0.08..+0.15): {net_h:+.4f}", None, -0.08 <= net_h <= 0.15, "[new]"),
        (f"'holds up' (R-shift >= -r = {-r:+.4f}): {'holds up' if rs_h >= -r else 'does not'}", 0.12, rs_h >= -r, "[orig 0.25]"),
        (f"K1 median 6 (0-15): median {st.median(k1)}, range {min(k1)}-{max(k1)}", None, 0 <= min(k1) and max(k1) <= 15, "[orig 3]"),
        (f"K2 median 50 (30-60): median {st.median(k2)}, range {min(k2)}-{max(k2)}", None, min(k2) >= 30, "[orig 35]"),
        (f"K2 >= alive at T-1 on some seed: {capped}/10", 0.55, capped >= 1, "[orig 0.3]"),
        (f"co-evolved |R-null| >= r and within 0.05 of R-shift, k>0 seeds ({len(kpos)}): R-null {rn:+.4f}, R-shift {rs_k:+.4f}", 0.65,
         abs(rn) >= r and abs(rn - rs_k) <= 0.05, "[orig 0.65]"),
        (f"R-body recovery +0.10 (-0.40..+0.60): {mean([w['rbody_shift'] for w in per]):+.4f}", None,
         -0.40 <= mean([w["rbody_shift"] for w in per]) <= 0.60, "[orig +0.7]"),
        (f"co-evolved shift paired recovery 'none' on >= 7/10: {hs.count('none')}/10", 0.65, hs.count("none") >= 7, "[orig P-form, 0.55]"),
        (f"designed shift paired recovery 'none' on >= 8/10: {cs.count('none')}/10", 0.70, cs.count("none") >= 8, "[orig 0.8]"),
        (f"co-evolved cull paired recovery <= 20 on >= 8/10: {sum(1 for d in hc if d != 'none' and int(d) <= 20)}/10", 0.60,
         sum(1 for d in hc if d != "none" and int(d) <= 20) >= 8, "[orig 0.7]"),
        (f"L(T+160) shift - cull within +-0.10, co-evolved (UNVALIDATED: V3 failed): {lline('shift-cull'):+.4f}", 0.50,
         abs(lline("shift-cull")) <= 0.10, "[orig 0.5]"),
        (f"falsifier (i), designed not bankrupt (recovery income >= 0.25, alive >= 12) on >= 3/10: {fals_i}/10 -> "
         f"{'FIRES' if fals_i >= 3 else 'does not fire'}", 0.65, fals_i >= 3, "[registered as the most exposed claim]"),
        (f"falsifier (ii), co-evolved fails (recovery income < 0.25) on >= 3/10: {fals_ii}/10 -> "
         f"{'FIRES' if fals_ii >= 3 else 'does not fire'}", None, fals_ii < 3, "[a HIT means it did not fire]"),
    ]
    for text, p, ok, note in rows:
        print(f"  {hit(ok)}  {'p ' + format(p, '.2f') if p is not None else 'point'}  {text}  {note}")
    probs = [(p, ok) for text, p, ok, _note in rows[3:] if p is not None and "UNVALIDATED" not in text]
    brier = mean([(p - (1 if ok else 0)) ** 2 for p, ok in probs])
    print(f"  Brier score over the {len(probs)} probability-stated binary predictions (class rows and the unvalidated carriage row excluded): {brier:.3f}")


if __name__ == "__main__":
    main()
