"""RBT-90 part 2, supplementary: the descent DAG at the pre-registered champion against the pre-registered pass.

The pre-registered part2_analyse.py called runs/RBT-84/descent.py without a NAME, so each descent.txt traces
the season-599 best rather than best_gen0590 (coordinator's 14:25 ruling: the pass stands as run, no scored
regularity reads it). descent590_one_seed.sh re-ran descent.py, unmodified, at best_gen0590's name into
descent-590.txt. This table sets the two side by side, from the committed text only.

    python runs/RBT-90/descent590_summary.py > runs/RBT-90/descent-590-summary.txt
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def last_json(path):
    for line in reversed(path.read_text().splitlines()):
        if line.startswith("{"):
            return json.loads(line)


ident = {}
restore = {}
for line in (HERE / "descent-590-identify.txt").read_text().splitlines():
    seed, rest = line.split("\t", 1)
    if rest.startswith("{"):
        ident[int(seed)] = json.loads(rest)
    else:
        restore[int(seed)] = rest.rsplit(": ", 1)[1]

print("RBT-90 part 2, supplementary descent pass: RBT-84 descent.py at the pre-registered champion (best_gen0590)")
print("against the pre-registered descent.txt (the season-599 best). Reported, read by no verdict.\n")
print("check = best_gen0590.json's name equals the unique best-fitness holistic row of lineage.jsonl at season 590")
print("        and history.json's best_name at season 590; restore = the unnamed call re-run on the restored bulk")
print("        against the committed descent.txt, byte for byte.\n")
hdr = f"{'seed':>5} {'champion':>8} {'599 best':>8} {'same':>4} {'check':>5} {'restore':>9} | {'verdict at 599':>15} {'verdict at 590':>15} | 599: anc fnd xov miss | 590: anc fnd xov miss"
print(hdr)
print("-" * len(hdr))
n_diff = n_verdict = 0
for s in SEEDS:
    arm = HERE / f"forage-{s}"
    if not (arm / "descent-590.txt").exists():
        print(f"{s:>5}  not traced (no descent-590.txt)")
        continue
    a, b, i = last_json(arm / "descent.txt"), last_json(arm / "descent-590.txt"), ident.get(s, {})
    assert b["champion"] == i.get("best_gen0590"), (s, b["champion"], i)
    same = a["champion"] == b["champion"]
    n_diff += not same
    n_verdict += a["verdict"] != b["verdict"]
    row = lambda d: f"{d['ancestors']:4d} {d['founders']:3d} {d['crossover_steps']:3d} {d['genomes_missing']:4d}"
    print(f"{s:>5} {b['champion']:>8} {a['champion']:>8} {'yes' if same else 'NO':>4} {'ok' if i.get('agree') else 'DIFF':>5} "
          f"{restore.get(s, '?'):>9} | {a['verdict']:>15} {b['verdict']:>15} |      {row(a)} |      {row(b)}")
print(f"\nseeds traced: {sum((HERE / f'forage-{s}' / 'descent-590.txt').exists() for s in SEEDS)} of {len(SEEDS)}; "
      f"season-599 best differs from the champion on {n_diff}; the descent verdict differs on {n_verdict}.")
