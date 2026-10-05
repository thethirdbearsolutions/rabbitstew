# RBT-134 lanes: shared preamble and helpers (sourced by laneA.sh and laneB.sh; see runs/RBT-134/LAUNCH.md).
#
# Exit codes: 3 no GO (RBT134_GO=1 unset), 4 dirty tree, 5 a stale output from another head, 6 a sub-command failed,
# 7 the output commit/push failed.  RBT134_DRY=1 prints the plan (what would run, what is skipped) and runs nothing.
# RBT134_NO_PUSH=1 skips the output commit (tests, or a manual commit).
set -uo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT" || exit 6
PY=${PYTHON:-python3}
WORKERS=${WORKERS:-4}
OUT=runs/RBT-134/out
RELAY="$PY runs/RBT-134/lanes/relay.py"

if [ "${RBT134_GO:-}" != "1" ]; then
  echo "refused: RBT-134 runs only after the coordinator's GO (set RBT134_GO=1)" >&2
  exit 3
fi
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "refused: the tree is dirty; run from a clean checkout of the GO sha" >&2
  exit 4
fi
HEAD=$(git rev-parse HEAD)
mkdir -p "$OUT"
echo "RBT-134 lane at $HEAD (clean tree)"
T0=$SECONDS

# step NAME CMD... : run CMD (or print it under RBT134_DRY=1); any failure stops the lane with exit 6
step() {
  local name=$1; shift
  if [ "${RBT134_DRY:-0}" = "1" ]; then echo "PLAN run $name: $*"; return 0; fi
  echo "run $name"
  "$@" || { echo "FAILED: $name ($*)" >&2; exit 6; }
}

# to_file NAME FILE CMD... : run CMD with stdout to FILE.tmp, renamed to FILE only on success (so FILE == complete)
to_file() {
  local name=$1 file=$2; shift 2
  if [ "${RBT134_DRY:-0}" = "1" ]; then echo "PLAN run $name: $* > $file"; return 0; fi
  echo "run $name"
  "$@" > "$file.tmp" || { echo "FAILED: $name ($*)" >&2; rm -f "$file.tmp"; exit 6; }
  mv "$file.tmp" "$file"
}

# check_json KIND FILE N : complete -> 0, incomplete -> 1, stale (written at another head) -> exit 5
check_json() {
  local state
  state=$($RELAY "complete-$1" "$2" "$HEAD" "$3")
  case "$state" in
    complete) return 0 ;;
    stale) echo "refused: $2 was written at another head; move it aside or restore that head" >&2; exit 5 ;;
    *) return 1 ;;
  esac
}

skip() { echo "${RBT134_DRY:+PLAN }skip $1 (complete)"; }

cpu_times() { times | tail -1; }

# commit_outputs BRANCH FILE... : commit the lane's outputs onto BRANCH (a fresh worktree at HEAD; the lane owns
# the branch, so a re-run replaces it) and push it, retrying network failures.
commit_outputs() {
  local branch=$1; shift
  if [ "${RBT134_DRY:-0}" = "1" ] || [ "${RBT134_NO_PUSH:-0}" = "1" ]; then
    echo "${RBT134_DRY:+PLAN }output commit to $branch skipped (dry run or RBT134_NO_PUSH=1)"; return 0
  fi
  local wt; wt=$(mktemp -d)/wt
  git worktree add -q --detach "$wt" "$HEAD" || exit 7
  mkdir -p "$wt/$OUT"
  for f in "$@"; do [ -f "$OUT/$f" ] && cp "$OUT/$f" "$wt/$OUT/$f"; done
  (
    cd "$wt" || exit 7
    git checkout -q -B "$branch" || exit 7
    git add -f "$OUT" || exit 7
    git commit -q -m "RBT-134 lane outputs ($branch) at $HEAD" || exit 7
    for i in 1 2 3 4 5; do
      git push -q -f origin "$branch" && exit 0
      sleep $((2 ** i))
    done
    exit 7
  ) || { git worktree remove --force "$wt"; echo "FAILED: output commit/push to $branch" >&2; exit 7; }
  git worktree remove --force "$wt"
  echo "outputs committed to $branch"
}
