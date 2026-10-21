# App plan (E0.8)

## Order of work

1. **S0.8.1 Builds on your phones.** Mirrors created; rename the app and bundle ids from `branding/brand.env`; own push setup (Firebase project for Android, APNs key for iOS; both keys stay out of git); TestFlight and the Android internal track. Point the server at Home Assistant's Tailscale address so it works away from home.
2. **S0.8.2 Home tab.** Rooms, scenes and device tiles live over HA's WebSocket API. Start from the Companion's existing native views; media cards for the TV, soundbars, Apple TV and Plex.
3. **S0.8.3 Assistant tab.** Text chat and push-to-talk to the same Claude agent as the voice devices, using HA's Assist API (`assist_pipeline/run`), which the Companion apps already speak. One history across voice and app.
4. **S0.8.4 Widgets and quick controls.** See `widgets.md`.
5. **S0.8.5 Fallback.** Telegram chat already works through Home Assistant (`home-assistant-config/packages/telegram.yaml`) while the app matures.

## Rules

- No analytics or third-party SDKs beyond what upstream ships; turn off upstream crash reporting or point it at your own project.
- No secrets in the mirrors: signing keys, `GoogleService-Info.plist`, `google-services.json` and API keys come from CI secrets or local ignored files.
- Keep upstream changes in small, separate commits so monthly syncs stay easy.

## Later phases

- Phase 1: Agents tab (task board, live view via noVNC, approvals with Face ID signed by a Secure Enclave key, take over, kill) and vault login release (E1.6, E1.7).
- Phase 2: hands-free voice and intercom over LiveKit.
