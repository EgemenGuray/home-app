# Design system: one look on every screen (S0.8.2)

The phone app, the web app and the Show screens should feel like one product, not stock Home Assistant. Most of the app *is* the HA frontend in a web view, so the skin lives in Home Assistant and the native screens copy its tokens.

| Surface | Where the look comes from |
|---|---|
| Web app, and the Home tab in the phone app (HA frontend) | `home-assistant-config/themes/home.yaml` (theme **Home**), applied to every user on start by `packages/skin.yaml`; dashboard `dashboards/home.yaml` |
| Show screens (kiosk) | Theme **Home Show** (always dark, larger radius) on `dashboards/show.yaml` |
| Native screens: Assistant tab, Agents tab, approvals, widgets, notifications | `branding/tokens.json`. Same values as the HA theme; change both together |

The look is identical in both setups, since HA and its dashboards are on the hub Mac either way.

## Tokens

Warm neutral backgrounds, one green (`primary`) for "on and fine", amber (`accent`) for "needs you" and for lights that are on, and red only for safety and failures. Cards have no borders, 20 px radius and a soft shadow. Use the system font: SF Pro on iOS, Roboto on Android. Light and dark follow the phone; the Show screens are always dark.

## Rules that keep it frictionless

1. **One tap does one thing.** Scene and device tiles act on tap; long-press opens details. No confirmation sheets, except approvals.
2. **Approvals: one push, one tap, Face ID.** The push says what will happen in plain words ("unlock front door") and how long it's valid. Tapping it opens straight to that request (`homeapp://approvals/<id>`). The app shows the summary with Approve as the default button, and Face ID signs it. It never shows an extra "are you sure?". Deny is one tap and needs no Face ID. The result then comes back where you asked: spoken in the room, or as a push.
3. **Always say what's happening.** Every request shows listening, thinking or done. A slow answer turns into "taking longer than usual" within 3 s, never silence. Failures say what still works, e.g. "Lights, timers and alarms still work."
4. **Same words everywhere.** Scenes are named the same on tiles, widgets and voice (Morning, Leaving, Movie, Good night), and they call the same scripts.
5. **Waiting for you is always one glance away.** Pending approvals and tasks waiting on you show as a badge on the Agents tab, and as the top card of the Assistant tab.
6. **No dead ends.** Every error screen has one next step: retry, open in the app, or take over.

## Native components

| Component | Spec |
|---|---|
| Approval card | Title (`summary`), job and agent, exit route and country, amount in CAD for purchases, time left. Buttons: Approve (primary, Face ID) and Deny |
| Task row | Title, state chip (queued, running, waiting for you in amber, done, failed in red), last step, time |
| Assistant bubble | Your text right-aligned on `surface_alt`; the assistant left-aligned on `surface`; approval chips inline |
| Take-over bar | Shown during live view: Pause, Take over, Hand back, Stop, with the elapsed time |
