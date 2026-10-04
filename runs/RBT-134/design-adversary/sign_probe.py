# Adversary probe: the `sign` artefact is not confined to |b_k| < 1e-9.  Edits committed arrivals only.
import importlib.util, sys
spec = importlib.util.spec_from_file_location("da", sys.argv[1]); da = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]] + sys.argv[2:]; spec.loader.exec_module(da)
sr = da.sr
import re
from rabbitstew.fixed import drive_effector_units
for readout, sigma in (("docs/artifacts/RBT-91-alone-baseline.txt", None), ("docs/artifacts/RBT-91-alone-4.0.txt", 4.0)):
    hits = re.findall(r"(\S+) lineage (\d+): \d+ unit\(s\), LINKS ALONE ([+-][\d.]+)", open(readout).read())
    for label, i, _ in hits:
        ph = da.regenerate(label, int(i), 19, 0.15, 0.1, sigma)
        k = sr.motif_units(ph)[0]
        if ph.units[k].unit.func != "sign": continue
        nL, nR = sr._wheel_noses(ph)
        w = {}
        for s, d, wt in ph.links: w[(s, d)] = w.get((s, d), 0.0) + wt
        half = abs(w[(nL, k)] - w[(nR, k)]) * sr.DRIVE / 2
        out = []
        for bk in (1e-9, 1e-4, 1e-3, 0.5 * half, 0.99 * half, 1.01 * half):
            out.append(f"{bk:.2e}:{abs(sr.links_alone_a(da.edited(ph, k, bk=bk), k)):.1f}")
        print(f"sigma={sigma or 0.4} {label} {i} |input to k at probe|={half:.4f}  b_k->|a|: " + "  ".join(out))
