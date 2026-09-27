#!/bin/bash
# RBT-120 pre-launch controls (PREREGISTRATION.md §7): on the launch tree, the full suite (the goldens: off is
# byte-identical; on, the Pioneer is byte-identical; budget.py's controls pass on a tiny O/B pair and each can fail)
# and the arm command.  Writes runs/RBT-120/controls/prelaunch.txt, which run_arm.sh requires.
set -e
cd "$(dirname "$0")/../.."
OUT=runs/RBT-120/controls/prelaunch.txt
{
  echo "# RBT-120 prelaunch $(date -u +%FT%TZ)"
  echo "rabbitstew_tree $(git rev-parse HEAD:rabbitstew)"
  python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')"
  python -c "import scipy" 2>/dev/null && echo "scipy PRESENT (the house venv has none)" || echo "scipy absent"
  echo "## arm command, B2 seed 5 line D:"
  python runs/RBT-120/world.py D - 5 runs/RBT-120/B2/5/D | tr '\0' ' '; echo
} > "$OUT"
if python -m pytest -q -p no:cacheprovider >> "$OUT" 2>&1; then echo "PRELAUNCH: PASS" >> "$OUT"; else echo "PRELAUNCH: FAIL" >> "$OUT"; exit 1; fi
tail -n 3 "$OUT"
