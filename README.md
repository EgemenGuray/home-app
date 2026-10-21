# home-app

The custom phone app and widgets (roadmap **E0.8**): one app on iOS and Android, built from the Home Assistant Companion apps so login, push notifications, widgets and Tailscale access come for free.

## Why mirrors, not GitHub forks

A GitHub fork of a public repo is always public. To keep the app private, the Companion repos are **mirrored** into two private repos, with the upstream kept as a second remote so fixes can be merged in:

| Private repo | Upstream | Language |
|---|---|---|
| `home-app-ios` | `home-assistant/iOS` | Swift |
| `home-app-android` | `home-assistant/android` | Kotlin |

This repo holds what the two share: the plan, branding, widget and screen specs, and the scripts that create and sync the mirrors. Both upstreams are Apache 2.0; keep their license and notices.

## Steps

1. `cp branding/brand.env.example branding/brand.env` and pick the app name and bundle id prefix (git-ignored).
2. On your laptop, with the GitHub CLI signed in: `./scripts/create-mirrors.sh`. It creates the two private repos and pushes the upstream history into them.
3. Grant the Claude GitHub App access to both, so the build work can continue there.
4. Apple Developer Program (about CA$141 a year) for TestFlight, and a Google Play developer account (one-time, about CA$35) for the internal track.
5. `./scripts/sync-upstream.sh <path-to-mirror>` monthly to merge upstream releases.

## Plan

See `docs/plan.md` (screens, widgets, order of work) and `docs/widgets.md`.
