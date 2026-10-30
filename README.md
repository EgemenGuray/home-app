# home-app

The custom phone app and widgets (roadmap **E0.8**): one app on iOS and Android, built from the Home Assistant Companion apps so login, push notifications, widgets and Tailscale access come for free.

## Two setups

The app is the same build for both. It reaches everything over Tailscale, and the server addresses are settings in the app.

| | **Mac mini only** | **Mac mini + Mac Studio** |
|---|---|---|
| Home and Assistant tabs, widgets | HA on the hub Mac | HA on the hub Mac (unchanged) |
| Agents tab (Phase 1) | Agent service on the hub Mac; live view of Linux workspaces on the rented VM | Agent service on the Studio; live view also of macOS VMs |
| Hands-free voice and intercom | Not available; push-to-talk through HA Assist | LiveKit to the Studio's voice server (`docs/voice-mode.md`) |
| Switching | Not applicable | Change the agent server address in settings; nothing to rebuild |

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

See `docs/plan.md` (screens, widgets, order of work), `docs/widgets.md`, `docs/agents-tab.md` (Phase 1 task board, approvals signed in the Secure Enclave, login release) and `docs/voice-mode.md` (Phase 2).
