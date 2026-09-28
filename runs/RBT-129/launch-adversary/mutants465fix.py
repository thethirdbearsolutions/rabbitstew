"""Mutants of #465's fixes (ec283bb) against its own tests/test_rbt129_launch.py (killed = some test fails, -x).
Run as: mutants465fix.py <venv python> <scratch checkout of ec283bb>.  One string edit each, reverted after."""
import subprocess, sys, os
PY, T = sys.argv[1], sys.argv[2]
P = os.path.join(T, "runs/RBT-129/launch/stages.py")
M = [
 ("M2a timeout never fires (communicate without timeout)", "out, _ = proc.communicate(timeout=limit)", "out, _ = proc.communicate()"),
 ("M2b kill durable.sh only, not its process group (the push lives on)", "os.killpg(proc.pid, signal.SIGKILL)", "proc.kill()"),
 ("M2c no retry after a timeout", "def save_now(d: str, label: str = None, retries: int = 1)", "def save_now(d: str, label: str = None, retries: int = 0)"),
 ("M2d a timeout returns 0", "    return 1 if code == \"timeout\" else code", "    return 0 if code == \"timeout\" else code"),
 ("M2e log written outside the lock (N-1)", "            finally:\n                fcntl.flock(lock, fcntl.LOCK_UN)", "            finally:\n                pass"),
 ("S2 periodic thread a daemon again", "name=f\"every {label}\").start()", "name=f\"every {label}\", daemon=True).start()"),
 ("M1a unit_status: no read of ckpt60's branch", "    text = branch_file(_label(os.path.join(unit, \"ckpt60\")), CKPT60_MARK)\n    return None if text is None else _from_marker(text)", "    return None"),
 ("M1b unit_status: the local ckpt60 marker ignored", "    if os.path.exists(mark):\n        return _from_marker(open(mark).read())\n    if os.path.exists(os.path.join(unit, UNIT)):", "    if False:\n        pass\n    if os.path.exists(os.path.join(unit, UNIT)):"),
 ("M1c _from_marker: every marker alive", "    return \"extinct\" if \"skipped: extinct pre-merge\" in text else \"alive\"", "    return \"alive\""),
 ("M1d check-branches --save: no backfill", "                backfill_record(os.path.dirname(d))", "                pass"),
 ("M1e backfill: K1.txt not copied", "    for name in (EXTINCT, \"K1.txt\"):", "    for name in (EXTINCT,):"),
 ("M1f --repo ignored", "        if a.repo:\n            set_repo(a.repo)", "        if False:\n            set_repo(a.repo)"),
 ("M1g branch_file reads the wrong member", "            f = tar.extractfile(f\"{name}/{member}\")", "            f = tar.extractfile(f\"{name}/MANIFEST\") if False else None"),
 ("S3a K1 verdict not in its marker (verdict path)", "        _mark(d, tag, f\"K1 {verdict}\")", "        _mark(d, tag)"),
 ("S3b K1 UNTESTABLE not in its marker", "            note += \"; K1 UNTESTABLE\"", "            pass"),
 ("S4 verify checks only worlds/config/<id>", "        for path in (os.path.join(root, \"worlds\", \"config\", pid, \"config.json\"), config_json_path(root, pid)):", "        for path in (os.path.join(root, \"worlds\", \"config\", pid, \"config.json\"),):"),
 ("S5 compass_dose_response.py unpinned", ", \"docs/artifacts/RBT-67/compass_dose_response.py\")", ")"),
 ("N3a fallback SEEN without the confirmation", "        return bool(pl.seen(rec))\n    s2 = rec.get(\"stage2\") or {}\n    conf = rec.get(\"confirm\") or rec.get(\"k3_confirm\") or {}\n    return bool(s2.get(\"c3\") and s2.get(\"c2\") and conf.get(\"c3\") and conf.get(\"c2\"))",
  "        return bool(pl.seen(rec))\n    s2 = rec.get(\"stage2\") or {}\n    conf = rec.get(\"confirm\") or rec.get(\"k3_confirm\") or {}\n    return bool(s2.get(\"c3\") and s2.get(\"c2\"))"),
 ("N3b fallback SEEN reads only 'confirm', not 'k3_confirm'", "    conf = rec.get(\"confirm\") or rec.get(\"k3_confirm\") or {}\n    return bool(s2.get(\"c3\") and s2.get(\"c2\") and conf.get(\"c3\") and conf.get(\"c2\"))\n\n\ndef _dt_sd",
  "    conf = rec.get(\"confirm\") or {}\n    return bool(s2.get(\"c3\") and s2.get(\"c2\") and conf.get(\"c3\") and conf.get(\"c2\"))\n\n\ndef _dt_sd"),
]
orig = open(P).read()
killed = 0
for name, a, b in M:
    if orig.count(a) != 1:
        print(f"{name}: NOT APPLIED (anchor found {orig.count(a)} times)", flush=True); continue
    open(P, "w").write(orig.replace(a, b))
    try:
        r = subprocess.run([PY, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tests/test_rbt129_launch.py"], cwd=T,
                           capture_output=True, text=True, env={**os.environ, "PYTHONPATH": T}, timeout=900)
        tail = [l for l in r.stdout.splitlines() if l.startswith("FAILED") or " passed" in l or " failed" in l][-2:]
        ok = r.returncode != 0
    except subprocess.TimeoutExpired:
        tail, ok = ["test run timed out (900 s)"], True
    killed += ok
    print(f"{name}: {'KILLED' if ok else 'SURVIVED'}  | {' / '.join(tail)[:220]}", flush=True)
    open(P, "w").write(orig)
for d, _, fs in os.walk(T):
    if "__pycache__" in d:
        for f in fs: os.remove(os.path.join(d, f))
print(f"{killed} of {len(M)} killed")
