"""RBT-112 design adversary re-check (F7, F11, F14) on #277 23232ef: gate.py's parse/decide and readout.py's verdict,
probed with synthetic RBT-106 H sections and counts built from RBT-106 readout.py's own print formats (l. 157, 160,
199, 234).  No arm output is read.  Usage (from the design checkout): recheck_probe.py"""
import importlib.util, sys
def load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); sys.modules[n] = m; s.loader.exec_module(m); return m
G = load("gate112", "runs/RBT-112/gate.py"); R = load("readout112", "runs/RBT-112/readout.py")
def sec(label, nU, nP, extra=""):
    return (f"\n## Pair H: HU (uniform) against HP (patchy), seeds 801, 4\n\nusable paired seeds: 9 of 10\n"
            f"HELD: HU {nU}, HP {nP};  paired log-excess at 599, HP - HU: +0.1 [-0.2, +0.4]\n{extra}"
            f"\nVERDICT H: {label}   [rules: ...]\n\n## Pair P: P1 (uniform) against S1 (patchy), seeds 801\n\nVERDICT P: P-NULL\n")
cases = [("SUPPORTED: x", 0, 4), ("SUPPORTED: x", 2, 5), ("FALSIFIED-b: x", 0, 1), ("FALSIFIED-b: x", 3, 1), ("FALSIFIED-b: x", 4, 0),
         ("NOT DECIDED at this n", 2, 3), ("NOT DECIDED at this n", 3, 4), ("FALSIFIED-a: x", 6, 6)]
print("## gate.py: every H label x nU")
for lab, nU, nP in cases:
    st, l, n = G.parse(sec(lab, nU, nP))
    print(f"  {lab.split(':')[0]:<22} nU={nU} nP={nP} -> {st} {l} nU={n} -> {G.decide(l, n)}")
st = G.parse(sec("VOID (fewer than 7 usable paired seeds)", 0, 0)); print(f"  VOID -> {st} -> decide {G.decide(st[1], st[2])} (-> hu_alone branch)")
st = G.parse("\n## Pair H: HU (uniform) against HP (patchy), seeds 801\n\nNOT READ: 3 arm(s) have not finished season 599: HU-3\n"); print(f"  NOT READ -> {st}")
st = G.parse(sec("NOT DECIDED at this n", 1, 2).replace("HELD: HU 1, HP 2;", "HELD: HU 1, HP 2; \nHELD: HU 4, HP 2;")); print(f"  duplicated HELD line -> {st}")
st = G.parse("VERDICT H: SUPPORTED\nHELD: HU 0, HP 5;\n"); print(f"  no H header -> {st}")
st = G.parse(sec("NOT DECIDED at this n", 1, 2) + sec("SUPPORTED: x", 0, 5)); print(f"  two H sections (the regex takes the first) -> {st}")
print("\n## readout.py verdict(nU, nZ, n_usable, n_lost)")
for a in [(0, 3, 10, 0), (2, 5, 10, 0), (2, 4, 10, 0), (0, 2, 10, 0), (0, 1, 10, 2), (0, 1, 10, 3), (0, 0, 7, 5), (1, 1, 6, 0), (3, 1, 10, 0)]:
    print(f"  nU={a[0]} nZ={a[1]} usable={a[2]} lost={a[3]} -> {R.verdict(*a).split(':')[0].split(' (')[0]}")
h = lambda n: {"n": n, "held": False}
print(f"\n## lost(): n 0/5 {R.lost({'held300': h(0), 'held599': h(5)})}; 5/0 {R.lost({'held300': h(5), 'held599': h(0)})}; "
      f"5/5 {R.lost({'held300': h(5), 'held599': h(5)})}; held-599 missing {R.lost({'held300': h(0), 'held599': None})}")
