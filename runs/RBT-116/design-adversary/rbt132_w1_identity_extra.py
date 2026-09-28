"""RBT-132 design adversary: W1 identity on the three code paths rbt132_w1_identity.py does not exercise, which RBT-132
changed: ``screen_draws`` (new default-season branch), ``_job`` (the CLI's worker, now a 4-tuple) and ``main`` (the CLI,
now passing the world and checking the fair marker).  steer.py at ce69f17 against the working tree.

    python runs/RBT-116/design-adversary/rbt132_w1_identity_extra.py > runs/RBT-116/design-adversary/rbt132_w1_identity_extra.txt

Fixture only: RBT-116's test fixture world (W1-shaped: G 2.5, tau 1 s, root + surface) with its season shortened to 3 s
to keep the 64-draw screen cheap; RBT-116's fixture bodies.  The screen draws W1's pool keys but runs only fixture
bodies in the fixture world; no RBT-116 host, gate cell or W1 world config.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
import importlib.util  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


src = subprocess.run(["git", "show", "ce69f17:runs/RBT-116/steer.py"], capture_output=True, text=True, cwd=ROOT, check=True).stdout
tmpd = tempfile.mkdtemp()
open(os.path.join(tmpd, "steer_base.py"), "w").write(src)
old = load("steer_base", os.path.join(tmpd, "steer_base.py"))
new = load("steer_now", os.path.join(ROOT, "runs", "RBT-116", "steer.py"))
T = load("t116", os.path.join(ROOT, "tests", "test_rbt116_steer.py"))
w1 = replace(T.FIXTURE, duration=3.0, food=replace(T.FIXTURE.food, eat_from="root", eat_rule="surface"))
hosts = [T.two_nose_steerer(), T.sensorless_mover()]

a = old.screen_draws(hosts, w1, "W1")
b = new.screen_draws(hosts, w1, "W1")
strip = lambda r: json.loads(json.dumps({k: (v.to_dict() if hasattr(v, "to_dict") else v) for k, v in r.items()}, default=str))
print(f"# screen_draws(W1): {'IDENTICAL' if strip(a) == strip(b) else 'DIFFERS'} "
      f"({len(b['table'])} draws, admissible {b['admissible']}, passed {b['passed']}, extended {b['extended']})")

bat = new.Battery(T.DRAWS[:4], T.DRAWS[4:20], T.DRAWS[20:36])
batd = bat.to_dict()
for g in hosts:
    ra = old._job((g.to_dict(), w1.to_dict(), batd))
    rb = new._job((g.to_dict(), w1.to_dict(), batd, "W1"))
    rc = new._job((g.to_dict(), w1.to_dict(), batd))
    print(f"# _job {g.name or 'fixture'}: old 3-tuple vs new 4-tuple (W1) {'IDENTICAL' if old._strip(ra) == new._strip(rb) else 'DIFFERS'}; "
          f"new 3-tuple {'IDENTICAL' if old._strip(ra) == new._strip(rc) else 'DIFFERS'} ({rb['call']})")

cfgp, batp, gp = (os.path.join(tmpd, f) for f in ("config.json", "battery.json", "g.json"))
json.dump({"sim": w1.to_dict()}, open(cfgp, "w"))
json.dump(batd, open(batp, "w"))
hosts[0].save(gp)
outs = []
for mod in (old, new):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.main(["--config", cfgp, "--battery", batp, "--world", "W1", gp])
    outs.append((rc, buf.getvalue()))
print(f"# main (the CLI) on W1: {'IDENTICAL' if outs[0] == outs[1] else 'DIFFERS'} stdout and exit code (exit {outs[1][0]}, {len(outs[1][1].splitlines())} lines)")
