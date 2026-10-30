# Hands-free voice and intercom (Phase 2, S2.4.2)

**Mac mini + Mac Studio only.** With the Mac mini only, the Assistant tab keeps push-to-talk through HA Assist and there is no intercom.

Once the voice server runs on the Studio, the Assistant tab gets a hands-free mode and the app joins room-to-room intercom (like Drop In), both as LiveKit participants. Use the LiveKit Swift and Android SDKs; the app gets a short-lived room token from the agent service over the tailnet. Interrupting a long answer (barge-in) is handled by the voice server, so the app only streams the microphone and plays audio.
