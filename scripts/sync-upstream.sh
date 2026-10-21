#!/usr/bin/env bash
# Merges the latest upstream Companion release into a mirror on a branch, for review as a PR.
# Usage: ./scripts/sync-upstream.sh <path-to-local-mirror-clone>
set -euo pipefail
cd "${1:?path to the local clone of home-app-ios or home-app-android}"
git remote get-url upstream >/dev/null 2>&1 || { echo "Add the upstream remote first (see create-mirrors.sh)." >&2; exit 1; }
git fetch upstream --tags
base=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|origin/||'); base=${base:-main}
branch="sync/upstream-$(date +%Y%m%d)"
git switch -c "$branch" "origin/$base"
git merge --no-ff --no-edit "upstream/$base" || { echo "Conflicts: resolve them, commit, then push $branch."; exit 1; }
git push -u origin "$branch"
echo "Pushed $branch; open a pull request and let CI build it before merging."
