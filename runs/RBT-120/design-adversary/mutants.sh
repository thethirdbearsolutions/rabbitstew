#!/bin/bash
# RBT-120 design adversary: can tests/test_rbt120.py fail?  Each mutant edits rabbitstew/ in the working tree, runs the
# new tests, and restores the file with git checkout.  Prints the failing-test count per mutant (0 = mutant survives).
cd "$(dirname "$0")/../../.."
run() {  # name file python-expr-to-apply
  python - "$2" "$3" "$4" <<'PY'
import sys; f, old, new = sys.argv[1:4]; s = open(f).read(); assert old in s, (f, old); open(f, "w").write(s.replace(old, new, 1))
PY
  r=$(python -m pytest -q -p no:cacheprovider tests/test_rbt120.py -x -k "not tiny_arm and not can_fail and not refuses" 2>&1 | tail -1)
  git checkout -q -- "$2"
  echo "$1: $r"
}
run "M1 gear not scaled"            rabbitstew/world.py "                    gear *= scale" "                    pass"
run "M2 damping keyed to unscaled"  rabbitstew/world.py "damping = config.joint_damping * (gear if is_driven" "damping = config.joint_damping * (gear / scale if is_driven"
run "M3 no servo clamp"             rabbitstew/world.py '    if not config.motor_budget:
        return {}
    return {"forcelimited"' '    return {}
    return {"forcelimited"'
run "M4 cap on 0.99 x own mass"     rabbitstew/world.py "cap = config.motor_budget * config.motor_strength * sum(p.mass for p in ph.parts)" "cap = 0.99 * config.motor_budget * config.motor_strength * sum(p.mass for p in ph.parts)"
run "M5 off key written"            rabbitstew/simulation.py '            del d["world"]["motor_budget"]' '            pass'
run "M6 evo off key written"        rabbitstew/evolution.py '            del d["sim"]["world"]["motor_budget"]' '            pass'
run "M7 cli ignores flag"           rabbitstew/cli.py "        cfg.world.motor_budget = args.motor_budget" "        pass"
run "M8 cap counts ball DOF once"   rabbitstew/world.py "for i, dof in sorted(driven)}" "for i, dof in sorted({(i, 0) for i, _ in driven})}"
