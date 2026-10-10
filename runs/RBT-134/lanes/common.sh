# RBT-134 lanes: shared preamble and helpers (sourced by laneA.sh and laneB.sh after they set LANE; see
# runs/RBT-134/LAUNCH.md).
#
# Exit codes: 3 no GO (RBT134_GO unset), 4 dirty tree or an untracked file outside out/, 5 the GO sha is not HEAD or
# an existing output was written at another head, 6 a sub-command failed, 7 the output commit/push failed or an
# output is missing, 8 (lane A) stopped at the control gate.  RBT134_DRY=1 prints the plan (what would run, what is
# skipped) and runs nothing.  RBT134_NO_PUSH=1 skips the output commit (tests, or a manual commit).
#
# No-peek (LAUNCH.md): every sub-command's stdout and stderr go to out/lane-$LANE.log (committed with the outputs),
# never to the console.  The console carries only "run X", "skip X (complete)", "FAILED: X", refusals and the RELAY.
set -uo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT" || exit 6
PY=${PYTHON:-python3}
WORKERS=${WORKERS:-4}
OUT=runs/RBT-134/out
LOG=$OUT/lane-$LANE.log
RELAY="$PY runs/RBT-134/lanes/relay.py"
HEAD=$(git rev-parse HEAD)

if [ -z "${RBT134_GO:-}" ]; then
  echo "refused: RBT-134 runs only after the coordinator's GO (set RBT134_GO=<the GO sha>)" >&2
  exit 3
fi
if [ "$RBT134_GO" != "$HEAD" ]; then
  echo "refused: RBT134_GO is not this checkout's HEAD; check out the GO sha" >&2
  exit 5
fi
if [ -n "$(git status --porcelain --untracked-files=all -- . ':(exclude)runs/RBT-134/out')" ]; then
  echo "refused: the tree is dirty or holds untracked files outside runs/RBT-134/out/; use a clean checkout of the GO sha" >&2
  exit 4
fi
mkdir -p "$OUT"
echo "RBT-134 lane $LANE: GO sha is HEAD, clean tree"
T0=$SECONDS
DRY=${RBT134_DRY:-0}
TIMESF=$(mktemp)
trap 'rm -f "$TIMESF"' EXIT

fail() { echo "FAILED: $1 (see $LOG)" >&2; exit 6; }

# step NAME CMD... : run CMD (or print the plan under RBT134_DRY=1), output to the log; a failure stops the lane (6)
step() {
  local name=$1; shift
  if [ "$DRY" = "1" ]; then echo "PLAN run $name: $*"; return 0; fi
  echo "run $name"
  echo "=== run $name: $*" >> "$LOG"
  "$@" >> "$LOG" 2>&1 || fail "$name"
}

# mark FILE : record the head FILE was completed at (FILE.head); written only after FILE is complete
mark() { [ "$DRY" = "1" ] || echo "$HEAD" > "$1.head"; }

# to_file NAME FILE CMD... : run CMD with stdout to FILE.tmp (stderr to the log), renamed to FILE only on success,
# then marked with HEAD
to_file() {
  local name=$1 file=$2; shift 2
  if [ "$DRY" = "1" ]; then echo "PLAN run $name: $* > $file"; return 0; fi
  echo "run $name"
  echo "=== run $name: $* > $file" >> "$LOG"
  "$@" > "$file.tmp" 2>> "$LOG" || { rm -f "$file.tmp"; fail "$name"; }
  mv "$file.tmp" "$file" && mark "$file"
}

# have_text FILE : 0 if FILE is complete at HEAD (skip it), 1 if neither FILE nor FILE.head exists (run it);
# anything else -- a foreign head, or a file without its head mark -- refuses (exit 5)
have_text() {
  [ -e "$1" ] || [ -e "$1.head" ] || return 1
  [ -f "$1" ] && [ "$(cat "$1.head" 2>/dev/null)" = "$HEAD" ] && return 0
  echo "refused: $1 was not completed at this head (no matching $1.head); move it aside" >&2
  exit 5
}

# check_json KIND FILE N [N_BG] : complete -> 0, incomplete -> 1, stale (another head, or no head) -> exit 5
check_json() {
  local state
  state=$($RELAY "complete-$1" "$2" "$HEAD" "$3" ${4:+"$4"})
  case "$state" in
    complete) return 0 ;;
    stale) echo "refused: $2 was not written at this head; move it aside or restore that head" >&2; exit 5 ;;
    *) return 1 ;;
  esac
}

skip() { if [ "$DRY" = "1" ]; then echo "PLAN skip $1 (complete)"; else echo "skip $1 (complete)"; fi; }

# cpu_now : children's user+sys CPU seconds so far into CPU_NOW.  `times` must run in this shell, not in a pipeline
# or $(...) subshell (whose children are its own, so it reads 0), hence the file.
cpu_now() {
  times > "$TIMESF"
  CPU_NOW=$(awk 'NR == 2 { s = 0; for (i = 1; i <= 2; i++) { split($i, t, /[ms]/); s += t[1] * 60 + t[2] }; printf "%d", s }' "$TIMESF")
}

# stage NAME : close the previous stage and open NAME ("" closes only); STAGES collects name:wall_s:cpu_s, which the
# RELAY prints rounded to the hour (a finer time could encode a count)
STAGES=()
STAGE=""
stage() {
  cpu_now
  if [ -n "$STAGE" ]; then STAGES+=("$STAGE:$((SECONDS - STAGE_T)):$((CPU_NOW - STAGE_C))"); fi
  STAGE=$1; STAGE_T=$SECONDS; STAGE_C=$CPU_NOW
}

# commit_outputs BRANCH FILE... : every FILE must exist (else exit 7); commit them onto BRANCH (a fresh worktree at
# HEAD; the lane owns the branch, so a re-run replaces it) and push, retrying network failures.  Sets COMMITTED.
COMMITTED=no
commit_outputs() {
  local branch=$1; shift
  [ "$DRY" = "1" ] && { echo "PLAN output commit to $branch"; return 0; }
  local f
  for f in "$@"; do
    [ -f "$OUT/$f" ] || { echo "FAILED: output $f is missing; nothing committed" >&2; exit 7; }
  done
  if [ "${RBT134_NO_PUSH:-0}" = "1" ]; then echo "output commit to $branch skipped (RBT134_NO_PUSH=1)"; return 0; fi
  local wt; wt=$(mktemp -d)/wt
  git worktree add -q --detach "$wt" "$HEAD" >> "$LOG" 2>&1 || { echo "FAILED: output worktree" >&2; exit 7; }
  mkdir -p "$wt/$OUT"
  (
    for f in "$@"; do cp "$OUT/$f" "$wt/$OUT/$f" || exit 7; done
    cd "$wt" || exit 7
    git checkout -q -B "$branch" || exit 7
    git add -f "$OUT" || exit 7
    git commit -q -m "RBT-134 lane outputs ($branch) at $HEAD" || exit 7
    for i in 1 2 3 4 5; do
      git push -q -f origin "$branch" && exit 0
      sleep $((2 ** i))
    done
    exit 7
  ) >> "$LOG" 2>&1 || { git worktree remove --force "$wt"; echo "FAILED: output commit/push to $branch" >&2; exit 7; }
  git worktree remove --force "$wt"
  COMMITTED=yes
  echo "outputs committed to $branch"
}

# relay STATUS : the RELAY block (all that may be relayed; LAUNCH.md)
relay() {
  $RELAY relay "$LANE" "$OUT" "$HEAD" --committed "$COMMITTED" --status "$1" "${STAGES[@]}" || {
    echo "FAILED: the RELAY block" >&2; exit 6; }
}
