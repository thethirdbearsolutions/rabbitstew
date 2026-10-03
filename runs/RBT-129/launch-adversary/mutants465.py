"""Mutants of PR #465's stages.py, each run against the PR's own tests/test_rbt129_launch.py (killed = some test fails).
Run as: mutants465.py <venv python> <scratch checkout of the trial merge>.  Each mutant is one string edit, reverted after."""
import subprocess, sys, os
PY, T = sys.argv[1], sys.argv[2]
P = os.path.join(T, "runs/RBT-129/launch/stages.py")
M = [
 ("S1 save: no lock", "            fcntl.flock(lock, fcntl.LOCK_EX)\n            r = subprocess.run(", "            r = subprocess.run("),
 ("S2 save: no retry", "def save_now(d: str, label: str = None, retries: int = 1)", "def save_now(d: str, label: str = None, retries: int = 0)"),
 ("S3 save: background save to /dev/null, unlogged (the Stage P failure)", "    t = threading.Thread(target=save_now, args=(d, label), name=f\"save {label or _label(d)}\")\n    t.start()\n    return t",
  "    subprocess.Popen([os.path.join(ROOT, 'scripts', 'durable.sh'), 'save', d, label or _label(d)], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n    return None"),
 ("S4 periodic loop outside the lock (durable.sh direct)", "        save_now(d, label, retries=0)", "        subprocess.run([os.path.join(ROOT, 'scripts', 'durable.sh'), 'save', d, label], cwd=ROOT, capture_output=True)"),
 ("S5 unit record not saved", "            f.write(text)\n    _save(rec)", "            f.write(text)"),
 ("S6 a short job not saved at its end", "    _save(d)  # every job, short ones included", "    long and _save(d)  # every job, short ones included"),
 ("E1 EXTINCT unit probed anyway", "                extinct.append(rel(unit))\n                continue", "                extinct.append(rel(unit))"),
 ("E2 unknown status taken as alive", "            if st is None:\n                unknown.append(rel(unit))\n                continue", "            if st is None:\n                pass"),
 ("E3 planted line after the probes", "        out.append(_guarded(po, _hosts(planted.format(", "(see below)"),
 ("K1a no marker on the verdict path", "        print(f\"{job['name']}: K1 {verdict}\")  # the control's verdict, not an outcome\n", "        print(f\"{job['name']}: K1 {verdict}\")  # the control's verdict, not an outcome\n        return\n"),
 ("K1b no marker on the UNTESTABLE path", "this unit has no season-60 state to fork\\n\")\n        _mark(", "this unit has no season-60 state to fork\\n\")\n            return\n        _mark("),
 ("B1 check-branches: no unit records expected", "                out[_label(rec)] = rec", "                pass"),
 ("B2 check-branches: always exit 0", "    return 1 if missing else 0", "    return 0"),
 ("B3 check-branches --save: no re-check after saving", "        have = remote_ckpt()\n        missing = sorted(k for k in want if k not in have)\n    for k in missing:", "    for k in missing:"),
 ("C1 calib-extract: stage-2 F leaked as an unlabelled number (appended column)", "            lines.append(f\"{kind:4s} {i:5d} {'yes' if _seen(r) else 'no':4s}  {cols[0]:8s}  {cols[1]:8s} {cols[2]:4s}  {cols[3]:8s}  {cols[4]:8s} {cols[5]}\")",
  "            lines.append(f\"{kind:4s} {i:5d} {'yes' if _seen(r) else 'no':4s}  {cols[0]:8s}  {cols[1]:8s} {cols[2]:4s}  {cols[3]:8s}  {cols[4]:8s} {cols[5]}  {f((r.get('stage2') or {}).get('F'))}\")"),
 ("C2 calib-extract: stage-2 F leaked in place of n", "                cols += [f(st.get(\"dT\")), f(_dt_sd(st)) if st else \"-\", str(st.get(\"n\", \"-\"))]",
  "                cols += [f(st.get(\"dT\")), f(_dt_sd(st)) if st else \"-\", str(st.get(\"F\", \"-\"))]"),
 ("C3 calib-extract: the call leaked as a digit (STEERS -> 1)", "        share.append(", "        lines.append(' '.join(str(int(r.get('call') == 'STEERS')) for r in recs))\n        share.append("),
 ("C4 calib runner prints planted.txt (F, calls, K3/K4)", "then cat {d}/calibration.txt; fi", "then cat {d}/calibration.txt {d}/planted.txt 2>/dev/null; fi"),
 ("C5 SD on n, not n-1, degrees of freedom", "_steer().t_quantile(0.95, n - 1)", "_steer().t_quantile(0.95, n)"),
 ("C6 SEEN without the confirmation", "    return bool(s2.get(\"c3\") and s2.get(\"c2\") and conf.get(\"c3\") and conf.get(\"c2\"))\n\n\ndef _dt_sd", "    return bool(s2.get(\"c3\") and s2.get(\"c2\"))\n\n\ndef _dt_sd"),
 ("C7 calibration cells: HP-G replaced by HP-L", "CALIB_CELLS = (\"c0-p030-PW-G\", \"c0-p030-HP-G\")", "CALIB_CELLS = (\"c0-p030-PW-G\", \"c0-p030-HP-L\")"),
 ("G1 guarded job's stdout reaches the runner", " > {d}/stdout.txt 2> {d}/stderr.txt || rc=$?;", " 2> {d}/stderr.txt || rc=$?;"),
]
orig = open(P).read()
killed = 0
for name, a, b in M:
    if orig.count(a) != 1:
        print(f"{name}: NOT APPLIED (anchor found {orig.count(a)} times)"); continue
    src = orig.replace(a, b)
    if name.startswith("E3"):  # emit each point's planted line after its probe lines, not before
        src = orig.replace("        out.append(_guarded(po, _hosts(planted.format(", "        _pl = (_guarded(po, _hosts(planted.format(")
        anchor = "rng=129300 + j, point=pid, out=o), hosts)))\n"
        assert src.count(anchor) == 1
        src = src.replace(anchor, anchor + "        out.append(_pl)\n")
    open(P, "w").write(src)
    r = subprocess.run([PY, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tests/test_rbt129_launch.py"], cwd=T,
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": T})
    tail = [l for l in r.stdout.splitlines() if l.startswith("FAILED") or " passed" in l or " failed" in l or "error" in l.lower()][-2:]
    ok = r.returncode != 0
    killed += ok
    print(f"{name}: {'KILLED' if ok else 'SURVIVED'}  | {' / '.join(tail)[:230]}", flush=True)
    open(P, "w").write(orig)
for d, _, fs in os.walk(T):
    if "__pycache__" in d:
        for f in fs: os.remove(os.path.join(d, f))
print(f"{killed} of {len(M)} killed")
