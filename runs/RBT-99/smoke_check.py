"""RBT-99 smoke check, read for nothing: does C2's shift do what it says, and only from its season?

Reads the two short runs of runs/RBT-99/smoke_runs.sh (plain; --shift-at 10 --shift work-cost=0.08;
20 seasons; RBT-90 part 2's command otherwise) and checks:

  identity    lineage.jsonl lines with season < 10, cohorts.jsonl lines with season < 10 and history.json
              entries with season < 10 are byte-identical (JSON-identical for history) to plain's
  config      the shift arm's config.json records shift_at 10 and shift work-cost=0.08
  history     entries carry "shift" from season 10 on and not before
  price       every lineage row's last_score equals food - w x work / 1000 (work in J) to the rows' 4-dp
              rounding, with w = 0.03 in both arms before season 10 and in plain throughout, and w = 0.08 in
              the shift arm from season 10; the check also fits w per (arm, season) and prints it

Nothing about income, deaths or alive is printed as a contrast: 20 seasons at one seed are read for nothing.

    python runs/RBT-99/smoke_check.py [DATA_DIR] [SEED] > runs/RBT-99/smoke.txt
"""
import json
import os
import sys

DATA = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-99/data"
SEED = sys.argv[2] if len(sys.argv) > 2 else "801"
EVENT = 10


def lines(path):
    with open(path, "rb") as f:
        return [l for l in f.read().split(b"\n") if l.strip()]


def main():
    P = os.path.join(DATA, f"smoke-plain-{SEED}")
    S = os.path.join(DATA, f"smoke-shift-{SEED}")
    ok = True
    print(f"RBT-99 smoke check, seed {SEED}, shift at {EVENT}: throwaway runs, read for nothing")
    for name, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
        a = [l for l in lines(os.path.join(P, name)) if json.loads(l)[key] < EVENT]
        b = [l for l in lines(os.path.join(S, name)) if json.loads(l)[key] < EVENT]
        same = a == b
        ok &= same
        print(f"  identity  {name:14s} pre-{EVENT} lines plain {len(a)} shift {len(b)}: {'IDENTICAL' if same else 'DIFFER'}")
    hp = json.load(open(os.path.join(P, "history.json")))["history"]
    hs = json.load(open(os.path.join(S, "history.json")))["history"]
    a = [e for e in hp if e["season"] < EVENT]
    b = [e for e in hs if e["season"] < EVENT]
    ok &= a == b
    print(f"  identity  history.json   pre-{EVENT} entries plain {len(a)} shift {len(b)}: {'IDENTICAL' if a == b else 'DIFFER'}")
    cfg = json.load(open(os.path.join(S, "config.json")))
    eco = cfg.get("ecology", cfg)
    good = eco.get("shift_at") == EVENT and str(eco.get("shift")).replace("food.work_cost", "work-cost") == "work-cost=0.08"
    ok &= good
    print(f"  config    shift_at {eco.get('shift_at')} shift {eco.get('shift')}: {'OK' if good else 'WRONG'}")
    seasons_with = sorted({e["season"] for e in hs if "shift" in e})
    good = seasons_with == list(range(EVENT, max(e["season"] for e in hs) + 1))
    ok &= good
    print(f"  history   'shift' on seasons {seasons_with[0] if seasons_with else None}..{seasons_with[-1] if seasons_with else None}"
          f" ({len(seasons_with)} seasons), value {hs[-1].get('shift')}: {'OK' if good else 'WRONG'}")
    for arm, path in (("plain", P), ("shift", S)):
        by = {}
        for l in lines(os.path.join(path, "lineage.jsonl")):
            r = json.loads(l)
            if "work" not in r or "food" not in r or r.get("death") == "cull":
                continue
            by.setdefault(r["generation"], []).append(r)
        bad, fits = 0, []
        for s in sorted(by):
            w_exp = 0.08 if (arm == "shift" and s >= EVENT) else 0.03
            num = den = 0.0
            for r in by[s]:
                if abs(r["last_score"] - (r["food"] - w_exp * r["work"] / 1000.0)) > 1e-3:
                    bad += 1
                num += (r["food"] - r["last_score"]) * r["work"] / 1000.0
                den += (r["work"] / 1000.0) ** 2
            fits.append((s, num / den if den else float("nan")))
        ok &= bad == 0
        pre = [w for s, w in fits if s < EVENT]
        post = [w for s, w in fits if s >= EVENT]
        print(f"  price     {arm}: rows off the expected price: {bad}; fitted w per season, pre-{EVENT} "
              f"{min(pre):.4f}..{max(pre):.4f}, from {EVENT} {min(post):.4f}..{max(post):.4f}")
    print(f"  MANIPULATION {'CONFIRMED' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()
