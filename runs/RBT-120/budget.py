"""RBT-120 registered readout (PREREGISTRATION.md §4-§7), fixed before any B arm runs.

    budget.py [--o-root runs/RBT-113] B_SEED_DIR [B_SEED_DIR ...]  > budget.txt

A B_SEED_DIR is `runs/RBT-120/B<k>/<seed>` (U/, D/, C/ `evolve` output directories, `final/` restored, and
`decompose.json` from decompose_budgeted.py).  Each is paired with RBT-113's default-operator seed directory at the
same seed, `<o-root>/O<k>/<seed>` (the O arm: the same command line without `--motor-budget`).  Statistics are
RBT-113's (readout.py, loaded unchanged): per line run and fauna the mean fitness m(t), the realised selection
differential S(t), and per seed directory b_div, b_up, b_down, h2 (raw yield per generation).

Controls (§7; any failure VOIDs every verdict below, since each touches the holistic data):
  K1  the B line's config.json is the O line's plus sim.world.motor_budget = 1.77, and nothing else;
  K2  the designed body is untouched: every conventional lineage row of every B line equals the O line's;
  K3  the holistic founders are the O arm's: generation-0 names and body-plan hashes equal;
  K4  the budget was operative: every holistic `final/` member of every B line, compiled under the run's own config,
      is within it (an implementation check on the real bodies; it also prints how many the budget had to scale);
  K5  RBT-113's own per-seed-directory controls and selection checks (readout.controls, selection_checks);
  K6  the run's tree: the arm's commit.txt `rabbitstew_tree` equals the tree this readout runs on (so K4's recompile is
      the physics the arm ran);
  K7  the servo clamp was live: some of the B seed directory's generation-0 holistic lineage rows (fitness, distance,
      descriptor vector) differ from the O directory's (the
      design adversary's probe_clamp predicts 7-19 of 40 moved per seed; a budget that never reached the run moves 0).
The manipulation is the MOTOR BUDGET: the Sum-gear cap AND the servo clamp (the design adversary's MUST 1: of RBT-113's
founders 6.5% are scaled by the cap but 34% change, 27.5% through the clamp alone).
Q1 (primary): the holistic divergence rate under the motor budget, b_div_B, raw and in RBT-113's FROZEN holistic sigma0,
    with RBT-113's verdict rule on the frozen scale: RESPONDS / NO RESPONSE at the powered effect / INCONCLUSIVE.
Q2 (registered test): how much of RBT-113's holistic response the budget removed, Delta = b_div_O - b_div_B per seed
    (holistic, raw), exact sign-flip: THE BUDGET LOWERS / RAISES THE HOLISTIC RESPONSE, NO CHANGE within +-0.05 sigma0,
    or INCONCLUSIVE.
Verdict precedence (the rules can overlap; the code tests in this order): Q1 RESPONDS, then NO RESPONSE, then
INCONCLUSIVE; Q2 LOWERS, then RAISES, then NO CHANGE, then INCONCLUSIVE.  A RESPONDS or LOWERS/RAISES whose CI lies
wholly inside +-0.05 sigma0 is printed with "(within the +-0.05 margin)".
Q3 (the RBT-117-style comparison) is RBT-117's compare.py, unchanged, through compare_budgeted.py.
"""
import argparse
import glob
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ro = _load("rbt113_readout", os.path.join(ROOT, "runs", "RBT-113", "readout.py"))
W = _load("rbt120_world", os.path.join(HERE, "world.py"))

ALPHA = ro.ALPHA
MOTOR_BUDGET = W.MOTOR_BUDGET
SIGMA0_REF = json.load(open(os.path.join(ROOT, "runs", "RBT-113", "sigma0_reference.json")))["holistic"]  # 0.221249, frozen by RBT-113
MARGIN = ro.EQUIV_OP  # 0.05 sigma0 per generation: RBT-113's equivalence margin, reused for Q2
MDE = ro.MDE_DIV      # 0.05 sigma0 per generation: RBT-113's NO RESPONSE bar, reused for Q1
KEYS = ("b_div", "b_up", "b_down", "h2", "h2_up", "h2_down", "b_C", "div_end")
SCOPE = ("This is the holistic fauna's response to imposed truncation selection on solo net yield under the motor budget "
         "(the Sum-gear cap, summed gear at most 1.77 x motor_strength x its own mass, the designed Pioneer's ratio rounded "
         "up, AND the servo clamp at +-gear); it is without the gear allowance and the servo wind-up, NOT without every "
         "lever: the Effector-bias walk (resting throttle) and free rotors on range-less ball joints stay open to both "
         "faunae. It is not a measurement of natural selection in the ecology, and h2 is a property of this design.")


def o_dir(bsd, o_root):
    _, _, seed = ro.parse_seed_dir(bsd)
    return os.path.join(o_root, f"O{(seed - 1) // 3 + 1}", str(seed))


def stats(sd):
    """RBT-113's statistics for one seed directory.  -> (seed, {fauna: arm_stats raw + final halves}, cfgs, runs, K5 failures)"""
    name, op, seed = ro.parse_seed_dir(sd)
    cfgs, runs = {}, {}
    for L in ro.LINES:
        cfgs[L], runs[L] = ro.read_run(os.path.join(sd, L))
    G = cfgs["U"]["generations"]
    wl = {L: ro.worlds(os.path.join(sd, L)) for L in ro.LINES}
    bad = [f"[{sc or 'both faunae'}] {m}" for sc, m in ro.controls(sd, cfgs, runs, G, wl)]
    st = {}
    for f in ro.FAUNAE:
        ser, S = {}, {}
        for L in ro.LINES:
            m, s_, sd0, _ = ro.line_series(runs[L][f])
            ser[L], S[L] = (m, s_), s_
        bad += [f"[{sc}] {m}" for sc, m in ro.selection_checks(f, S)]
        st[f] = dict(ro.arm_stats(ser), sd0=sd0, UC=float(ser["U"][0][-1] - ser["C"][0][-1]), CD=float(ser["C"][0][-1] - ser["D"][0][-1]),
                     Cdrift=float(ser["C"][0][-1] - ser["C"][0][0]))
    return seed, st, cfgs, runs, bad


def k1(cfg_b, cfg_o):
    b = json.loads(json.dumps(cfg_b))
    got = b["sim"]["world"].pop("motor_budget", None)
    if got != MOTOR_BUDGET:
        return f"motor_budget {got}, registered {MOTOR_BUDGET}"
    if "motor_budget" in cfg_o["sim"]["world"]:
        return "the paired O config carries a motor budget"
    if b != cfg_o:
        diff = sorted(k for k in set(b) | set(cfg_o) if b.get(k) != cfg_o.get(k))
        return f"config differs from the O arm's beyond the budget: {diff}"
    return None


def k4(sd, cfg):
    """Every holistic final/ member of every line within the budget, as compiled.  -> (failure message or None,
    {line: share of members over the budget before it scaled them})"""
    from rabbitstew import motors
    from rabbitstew.evolution import EvolutionConfig, generation_sim
    from rabbitstew.genotype import Genotype
    sim = generation_sim(EvolutionConfig.from_dict(cfg), 1131)
    worst, n, scaled = 0.0, 0, {}
    for L in ro.LINES:
        files = sorted(glob.glob(os.path.join(sd, L, "holistic", "final", "*.json")))
        if not files:
            return f"{L}/holistic/final is empty (restore the checkpoint; RUNNER §6)", {}
        caps = [motors.capacity(Genotype.load(p), sim) for p in files]
        worst = max([worst] + [c.ratio for c in caps])
        scaled[L] = sum(c.unbudgeted_ratio > MOTOR_BUDGET for c in caps) / len(caps)
    if worst > MOTOR_BUDGET * (1 + 1e-4):  # the MJCF writes gears to 6 significant figures
        return f"a final member at summed gear / (ms x mass) {worst:.4f} > {MOTOR_BUDGET}", scaled
    return None, scaled


def controls(bsd, osd):
    """K1-K7 for one B seed directory against its O pair.  -> ([failure messages], B stats, O stats)"""
    seed, sb, cb, rb, bad = stats(bsd)
    seed_o, so, co, rbo, bad_o = stats(osd)
    fails = [f"K5 {m}" for m in bad]
    if seed_o != seed:
        fails.append(f"paired with the O directory of seed {seed_o}")
    for L in ro.LINES:
        m = k1(cb[L], co[L])
        if m:
            fails.append(f"K1 {L}: {m}")
        if rb[L]["conventional"] != rbo[L]["conventional"]:
            fails.append(f"K2 {L}: the designed body's lineage differs from the O arm's (the budget reached the Pioneer, or the run is not the O arm's)")
    g0 = lambda runs: [(r["name"], r["body"]) for r in runs["U"]["holistic"] if r["generation"] == 0]  # noqa: E731
    if g0(rb) != g0(rbo):
        fails.append("K3 the holistic founders (generation-0 names and body-plan hashes) differ from the O arm's")
    tree = _tree()
    arm_commit = os.path.join(os.path.dirname(os.path.abspath(bsd.rstrip("/"))), "commit.txt")
    ran = dict(l.split(None, 1) for l in open(arm_commit).read().splitlines() if " " in l and not l.startswith("#")) if os.path.exists(arm_commit) else {}
    if ran.get("rabbitstew_tree", "").strip() != tree:
        fails.append(f"K6 the arm ran on rabbitstew tree {ran.get('rabbitstew_tree', '(no commit.txt)').strip()}, this readout is on {tree}")
    f0 = lambda runs: [r for r in runs["U"]["holistic"] if r["generation"] == 0]  # noqa: E731  whole rows: fitness, distance, vector
    moved = sum(a != b for a, b in zip(f0(rb), f0(rbo)))
    if moved == 0:
        fails.append("K7 no holistic founder's generation-0 row moved: the servo clamp (and the cap) did not reach the run")
    m, scaled = k4(bsd, cb["U"])
    if m:
        fails.append(f"K4 {m}")
    sb["holistic"]["over"] = scaled
    sb["holistic"]["moved0"] = moved
    return fails, sb, so


def _tree():
    """The rabbitstew/ tree this readout runs on (git), for K6."""
    import subprocess
    return subprocess.run(["git", "rev-parse", "HEAD:rabbitstew"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def decide_q1(u):
    """RBT-113's verdict rule on b_div in the frozen sigma0.  u: per-seed b_div (raw)."""
    s = [x / SIGMA0_REF for x in u]
    m, lo, hi, n = ro.t_ci(s)
    p = ro.sign_flip_p(s)
    if lo > 0 and p < ALPHA:
        return "RESPONDS" + (f" (within the +-{MDE} margin)" if hi < MDE else ""), p
    if hi < MDE:
        return f"NO RESPONSE at the powered effect (the CI excludes {MDE} sigma0 per generation)", p
    return "INCONCLUSIVE", p


def decide_q2(delta):
    """delta: per-seed b_div_O - b_div_B (raw)."""
    s = [x / SIGMA0_REF for x in delta]
    m, lo, hi, n = ro.t_ci(s)
    p = ro.sign_flip_p(s)
    if n < 2:
        return "NOT RUN", p
    inside = f" (within the +-{MARGIN} margin)" if -MARGIN < lo and hi < MARGIN else ""
    if lo > 0 and p < ALPHA:
        return f"THE BUDGET LOWERS THE HOLISTIC RESPONSE by {m:+.3f} [{lo:+.3f}, {hi:+.3f}] sigma0/generation{inside}", p
    if hi < 0 and p < ALPHA:
        return f"THE BUDGET RAISES THE HOLISTIC RESPONSE by {-m:+.3f} [{-hi:+.3f}, {-lo:+.3f}] sigma0/generation{inside}", p
    if -MARGIN < lo and hi < MARGIN:
        return f"NO CHANGE within +-{MARGIN}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]", p
    return f"INCONCLUSIVE: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]", p


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--o-root", default=os.path.join(ROOT, "runs", "RBT-113"))
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    print(f"# RBT-120 readout (runs/RBT-120/budget.py, fixed before any B arm ran); motor budget {MOTOR_BUDGET}; "
          f"frozen holistic sigma0 {SIGMA0_REF:.6f} (RBT-113)")
    seeds, fails, B, O, decs = [], [], {}, {}, {}
    for bsd in a.seed_dirs:
        name, op, seed = ro.parse_seed_dir(bsd)
        if op or seed in seeds or W.ARM_OF.get(seed) != os.path.basename(os.path.dirname(os.path.abspath(bsd.rstrip("/")))):
            raise SystemExit(f"{bsd}: not a registered B seed directory (default operator, seed under its arm {W.ARM_OF.get(seed)}, once)")
        osd = o_dir(bsd, a.o_root)
        f, sb, so = controls(bsd, osd)
        seeds.append(seed)
        B[seed], O[seed] = sb["holistic"], so["holistic"]
        for sd, tag in ((bsd, "B"), (osd, "O")):
            p = os.path.join(sd, "decompose.json")
            decs[(tag, seed)] = json.load(open(p)) if os.path.exists(p) else None
        fails += [f"seed {seed}: {m}" for m in f]
        over = ("  budget binding on " + ", ".join(f"{L} {v:.0%}" for L, v in sb["holistic"].get("over", {}).items()) + " of final members; "
                f"{sb['holistic'].get('moved0', 0)} holistic founders' generation-0 rows moved (K7)")
        print(f"seed {seed:3d} (B {bsd} | O {osd}) controls K1-K7 {'PASS' if not f else 'FAIL'}{over}" + "".join(f"\n    {m}" for m in f))
    seeds.sort()
    missing = sorted(set(W.ARM_OF) - set(seeds))
    if missing:
        print(f"WARNING: seeds missing from the 12 registered: {missing}; n = {len(seeds)}")
    void = bool(fails)

    print(f"\n## per seed, holistic, raw yield per generation (O = RBT-113's default-operator line, the same command without the budget)")
    print(f"  {'seed':>4s} " + " ".join(f"{k + '_B':>9s}" for k in ("b_div", "b_up", "b_down", "h2")) + " "
          + " ".join(f"{k + '_O':>9s}" for k in ("b_div", "b_up", "b_down", "h2")) + f" {'Delta':>9s}")
    for s in seeds:
        print(f"  {s:4d} " + " ".join(f"{B[s][k]:+9.5f}" for k in ("b_div", "b_up", "b_down", "h2")) + " "
              + " ".join(f"{O[s][k]:+9.5f}" for k in ("b_div", "b_up", "b_down", "h2")) + f" {O[s]['b_div'] - B[s]['b_div']:+9.5f}")

    print(f"\n## across seeds: mean [95% t CI] (n), sign-flip p; raw yield per generation, then frozen sigma0 units")
    for tag, T in (("B (budgeted)", B), ("O (RBT-113, salt 0)", O)):
        print(f"  {tag}")
        for k in KEYS:
            v = [T[s][k] for s in seeds]
            scaled = k.startswith("b_") or k == "div_end"
            print(f"    {k:8s} {ro.ci_text(v, '+.5f')}  p = {ro.sign_flip_p(v):.4f}"
                  + (f"   sigma0 {ro.ci_text([x / SIGMA0_REF for x in v], '+.4f')}" if scaled else ""))

    q1, p1 = decide_q1([B[s]["b_div"] for s in seeds])
    if void:
        q1 = "VOID (a control failed; see above)"
    hb = ro.t_ci([B[s]["b_div"] for s in seeds])
    ho = ro.t_ci([O[s]["b_div"] for s in seeds])
    print(f"\n## Q1 (primary): the holistic selection response under the motor budget (Sum-gear cap + servo clamp)")
    print(f"  b_div_B {hb[0]:+.5f} [{hb[1]:+.5f}, {hb[2]:+.5f}] yield per generation = {hb[0] / SIGMA0_REF:+.4f} "
          f"[{hb[1] / SIGMA0_REF:+.4f}, {hb[2] / SIGMA0_REF:+.4f}] frozen sigma0; p = {p1:.4f}")
    print(f"  (RBT-113's salt-0 holistic lines at the same seeds, unbudgeted: {ho[0]:+.5f} [{ho[1]:+.5f}, {ho[2]:+.5f}])")
    print(f"  VERDICT Q1: {q1}")

    delta = [O[s]["b_div"] - B[s]["b_div"] for s in seeds]
    q2, p2 = decide_q2(delta)
    if void:
        q2 = "VOID (a control failed; see above)"
    share = float(np.mean(delta) / np.mean([O[s]["b_div"] for s in seeds])) if seeds else float("nan")
    print(f"\n## Q2 (registered test): how much of RBT-113's holistic response the motor budget (cap + servo clamp) removed, Delta = b_div_O - b_div_B, paired by seed")
    print(f"  Delta {ro.ci_text(delta, '+.5f')} yield per generation; exact sign-flip p = {p2:.4f}; "
          f"share of the O lines' b_div: {share:.0%}")
    for k in ("b_up", "b_down", "h2"):
        v = [O[s][k] - B[s][k] for s in seeds]
        print(f"  {k:8s} O - B {ro.ci_text(v, '+.5f')}  p = {ro.sign_flip_p(v):.4f}   (descriptive)")
    print(f"  VERDICT Q2: {q2}")

    print(f"\n## food/work at the final generation (decompose.json, 4 fixed draws; descriptive, not scored)")
    for tag in ("B", "O"):
        if all(decs[(tag, s)] is not None for s in seeds) and seeds:
            fu = ro.food_units({s: decs[(tag, s)] for s in seeds}, "holistic", [[s] for s in seeds])
            for g in ("founders", "U", "D", "C"):
                print(f"  {tag} {g:8s} food {ro.ci_text([x[g + ' food'] for x in fu], '.3f')}  work {ro.ci_text([x[g + ' work'] for x in fu], '.3f')}  net {ro.ci_text([x[g + ' net'] for x in fu])}")
            for c in ("U-D", "U-C", "C-D"):
                df, dw = [x[f"{c} food"] for x in fu], [x[f"{c} work"] for x in fu]
                print(f"  {tag} {c:4s} delta food {ro.ci_text(df)}  delta work {ro.ci_text(dw)}  food share {ro.food_share(df, dw):.0%}")
        else:
            print(f"  {tag}: NOT YET RUN (decompose.json missing)")

    print(f"\n## HEADLINE: under the motor budget (Sum-gear cap {MOTOR_BUDGET} + servo clamp), over {len(seeds)} seeds, the holistic up and down lines diverged by "
          f"{ro.ci_text([B[s]['b_div'] / SIGMA0_REF for s in seeds])} frozen sigma0 per generation ({hb[0]:+.4f} yield per "
          f"generation), against {ho[0] / SIGMA0_REF:+.3f} for the same seeds without it; Q1: {q1}; Q2: {q2}.")
    print(f"  {SCOPE}")
    return 1 if void else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
