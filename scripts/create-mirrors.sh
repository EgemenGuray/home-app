#!/usr/bin/env bash
# Creates private mirrors of the HA Companion apps under your GitHub account (S0.8.1).
# Run on your laptop with `gh auth login` done. Safe to re-run: skips repos that exist.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
BRAND_ENV="${BRAND_ENV:-$HERE/branding/brand.env}"
[[ -f "$BRAND_ENV" ]] || { echo "Copy branding/brand.env.example to branding/brand.env and fill it in." >&2; exit 1; }
# shellcheck disable=SC1090
source "$BRAND_ENV"
: "${GITHUB_OWNER:?set GITHUB_OWNER}" "${IOS_REPO:?set IOS_REPO}" "${ANDROID_REPO:?set ANDROID_REPO}"
[[ "$GITHUB_OWNER" != your-github-login ]] || { echo "Set GITHUB_OWNER in $BRAND_ENV to your GitHub login." >&2; exit 1; }
command -v gh >/dev/null || { echo "Install the GitHub CLI (brew install gh) and run gh auth login." >&2; exit 1; }

mirror() {
  local upstream="$1" target="$2" desc="$3"
  if gh repo view "$GITHUB_OWNER/$target" >/dev/null 2>&1; then
    echo "$GITHUB_OWNER/$target exists; skipping."; return
  fi
  gh repo create "$GITHUB_OWNER/$target" --private --description "$desc" --disable-wiki
  local tmp; tmp=$(mktemp -d)
  git clone --bare "https://github.com/$upstream.git" "$tmp/src.git"
  # Only branches and tags; upstream pull-request refs are left out.
  git -C "$tmp/src.git" push "https://github.com/$GITHUB_OWNER/$target.git" 'refs/heads/*:refs/heads/*' 'refs/tags/*:refs/tags/*'
  rm -rf "$tmp"
  echo "Created private mirror $GITHUB_OWNER/$target from $upstream"
}

mirror home-assistant/iOS "$IOS_REPO" "Private app (iOS), mirrored from the HA Companion app"
mirror home-assistant/android "$ANDROID_REPO" "Private app (Android), mirrored from the HA Companion app"

echo
echo "Next: clone each, then add the upstream remote:"
echo "  git remote add upstream https://github.com/home-assistant/iOS.git      # or android"
echo "  git remote set-url --push upstream DISABLED   # never push to upstream by accident"
