"""C3-5 counterfactual from the public Stage-1 record only (stage1_readout.txt L339-L373, the regime table).
regime.py's viability = net_per_birth / living_cost, so the O-5 per-birth income = 0.25 * (viability + 1).
Window 180 (h180/c180) is the plan's uncensored cohort; window 240 is the registered (censored) one.
The table's viability is the mean over the arm's seeds (n printed per line), printed to 2 decimals."""
import re
for l in open("runs/RBT-129/stage1-readout/stage1_readout.txt").read().splitlines()[338:373]:
    if " S (n" not in l:
        continue
    pid = l.split()[0]
    d = dict(re.findall(r"([hc]\d+): ([^ ]+)", l))
    def pb(k):
        v = d[k].split("/")[1]
        return None if v == "--" else 0.25 * (float(v) + 1)
    vals = [pb(k) for k in ("h180", "c180", "h240", "c240")]
    f = lambda x: "--" if x is None else f"{x:+.3f}"
    mg = lambda a, b: "--" if a is None or b is None else ("MARGINAL" if min(a, b) < 0.25 else ("edge" if min(a, b) == 0.25 else "-"))
    print(f"{pid:14s} 180-239: H {f(vals[0])} D {f(vals[1])} {mg(vals[0], vals[1]):8s} | 240-299: H {f(vals[2])} D {f(vals[3])} {mg(vals[2], vals[3])}")
