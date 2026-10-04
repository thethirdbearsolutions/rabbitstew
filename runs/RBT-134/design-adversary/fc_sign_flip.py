# Fix-check (r2): does r2's sign_flip fire exactly inside the window, and does the excluded probe ever count?
# Edits committed RBT-91 arrivals only (default and sigma 4.0).  Usage: fc_sign_flip.py <r2 decompose_arrivals.py>
import importlib.util, sys, re
spec = importlib.util.spec_from_file_location("da", sys.argv[1]); da = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], "--readout", "x"]; spec.loader.exec_module(da)
sr = da.sr
miss = 0; false_flag = 0; n = 0
for readout, sigma in (("docs/artifacts/RBT-91-alone-baseline.txt", None), ("docs/artifacts/RBT-91-alone-4.0.txt", 4.0)):
    for label, i, _ in re.findall(r"(\S+) lineage (\d+): \d+ unit\(s\), LINKS ALONE ([+-][\d.]+)", open(readout).read()):
        ph = da.regenerate(label, int(i), 19, 0.15, 0.1, sigma)
        k = sr.motif_units(ph)[0]
        if ph.units[k].unit.func != "sign": continue
        nL, nR = sr._wheel_noses(ph)
        w = {}
        for s, d, wt in ph.links: w[(s, d)] = w.get((s, d), 0.0) + wt
        half = abs(w[(nL, k)] - w[(nR, k)]) * sr.DRIVE / 2
        row = []
        for bk in (0.0, 1e-3, 0.5 * half, 0.99 * half, 1.01 * half, 0.5, -0.99 * half, -1.01 * half):
            e = da.edited(ph, k, bk=bk)
            a = abs(sr.links_alone_a(e, k)); f = da.sign_flip(e, k); n += 1
            inside = abs(bk) < half
            miss += (inside and a > 1e-9 and not f)        # an artefact reading the flag missed
            false_flag += (f and not inside)
            row.append(f"{bk:+.4f}:{a:.1f}{'F' if f else '-'}")
        print(f"sigma={sigma or 0.4} {label} {i} window={half:.4f}  " + "  ".join(row))
print(f"probes {n}: artefact readings NOT flagged {miss}; flags outside the window {false_flag}")
