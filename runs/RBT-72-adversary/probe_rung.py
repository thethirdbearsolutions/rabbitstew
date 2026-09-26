"""RBT-72 adversary: measure the 'paying rung' 6.8664 that runs/RBT-91/structural_rate.py
hard-codes (line ~346) and that no committed readout prints. Same install, same host and
same probe as its self-test (P-801 gen 590, genotype_motif.install), at w = 8, 16, 32,
both signs, whole brain and links alone. No simulation; about a second."""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sr", os.path.join(HERE, "..", "RBT-91", "structural_rate.py"))
sr = importlib.util.module_from_spec(spec); sys.argv = ["x"]; spec.loader.exec_module(sr)
gspec = importlib.util.spec_from_file_location("gm", os.path.join(HERE, "..", "..", "scripts", "genotype_motif.py"))
gm = importlib.util.module_from_spec(gspec); gspec.loader.exec_module(gm)
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

cfg = SimConfig.from_dict(json.load(open("runs/RBT-19/P-801/config.json"))["sim"])
g = Genotype.load("runs/RBT-19/P-801/conventional/best_gen0590.json")
print(f"bare parent: whole brain {sr.small_signal_a(synthesize(g, cfg.synthesis)):+.4f}")
for w in (8.0, 16.0, 32.0):
    row = []
    for sign in (+1.0, -1.0):
        ph = synthesize(gm.install(g, w, sign=sign), cfg.synthesis)
        k = sr.motif_units(ph)[0]
        row.append((sr.small_signal_a(ph), sr.links_alone_a(ph, k)))
    (wp, ap), (wn, an) = row
    print(f"w={w:4.0f}: whole brain +1 {wp:+.4f} / -1 {wn:+.4f} (antisymmetric part {(wp - wn)/2:.4f}); "
          f"links alone +1 {ap:+.4f} / -1 {an:+.4f}; linear 2w {2*w:.0f}")
