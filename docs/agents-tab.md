# Agents tab and phone approvals (E1.6, E1.7)

The app is the only place anything risky can be approved. The approval and login flows below are identical in both setups. Only the agent service's address changes (the hub Mac with the Mac mini only, the Studio with the Mac mini + Mac Studio), and the broker stays on the hub Mac either way. The server side is in home-agents (`approvals.py`, `broker.py`, `api.py`); this is the app's half of the contract.

## Screens

- **Task board:** queued, running, waiting for you, done, failed (`GET /v1/jobs`).
- **Screen** per agent with a desktop: watch it work, take over, hand back. See "Screen share and take over" below.
- **Pause, resume, kill.** Kill destroys the workspace and keeps the log.
- **Approvals:** one push per request, sent by the agent service through HA's `notify.owner_phone`. Tapping it opens `homeapp://approvals/<id>` straight on that request, and Face ID signs Approve; there is no second confirmation (`design-system.md`). Shows the job, the site, the exit IP and country, and the planned action in plain words. Purchases show merchant, item and amount in CAD. Once signed, the action runs at once, and the result is spoken in the room that asked or pushed back to the phone.
- **Audit search** over tool calls, messages, approvals, logins and takeovers.

## Screen share and take over

Works like sharing one Mac with an agent: the agent drives while you watch, and one touch gives you the wheel. The desktop has one pointer and one keyboard, so only one side drives at a time. The server half is in home-agents (`takeover.py`, `screen_relay.py`, `screen_api.py`).

| You see | Meaning |
|---|---|
| Green glow around the screen | The agent is driving |
| Amber edge | You are driving |
| Grey edge | Paused: nobody drives |

- **Banner** above the screen: the task, who is driving, the last three steps, time in this state, and **Take over**, **Pause**, **Hand back** (with an optional "what I did" note) and **Stop task**.
- **Touch to take over.** While the agent drives, the screen is view only; the first touch, click or key takes over. The agent finishes the step it is on and waits before the next one.
- **Hand back.** The agent resumes with a note: how long you drove, your note, and an instruction to look at the screen again before acting, so it doesn't redo what you did.
- **Walk away safely.** If you take over and stop touching for 10 minutes, the screen pauses (never back to the agent) and you get a push.
- **Lock Screen.** A Live Activity while an agent has a screen open: the task, who is driving, and a Pause button (`POST /v1/screens/<ws>/pause`, no Face ID: it only ever stops the agent).
- **Agents tab badge** on any agent whose screen is open, and the screen is one tap from the task card and from a "needs you" push (CAPTCHA, passkey-only site).

How the app talks to it:

1. `GET /v1/screens` lists open screens; `GET /v1/screens/<ws>` is the banner (poll every 2 s, or on each task event).
2. `POST /v1/screens/<ws>/ticket {"mode":"view"}` returns a ticket and the relay URL. Open a WebSocket to `<url>?ticket=<ticket>&notices=1` and give it to noVNC (`new RFB(el, socket)`) with `viewOnly` on.
3. On the first touch: `POST /v1/screens/<ws>/take`, then send `{"ticket":"<control ticket>"}` as a text frame on the same socket. No reconnect. Every 30 s, renew with `POST .../ticket {"mode":"control"}` and send it the same way. Control tickets last 60 s, so a lost phone stops driving within a minute.
4. **Hand back:** `POST /v1/screens/<ws>/hand-back {"text": "..."}`, then close the socket and reopen it with a view ticket, so control ends at once.
5. With `notices=1` the relay answers each upgrade and tells you once when it dropped your input; show "Tap Take over" then. Without it (noVNC in a browser) it sends only VNC frames.

The same flow works in a browser at `/screen` on the agent service: the web app, or Safari on the phone before the native screen ships. It asks for the service token like the console and loads noVNC from the agent service itself, never from a CDN.

**Mac mini only:** the screen relay runs on the rented workspace VM next to the Linux desktops; the app reaches it on port 8710 over the tailnet (home-infra's tailnet policy allows only your devices). Linux desktops only.
**Mac mini + Mac Studio:** the relay runs on the Studio for its Docker desktops; set `SCREEN_RELAY_URL` to the Studio. macOS VMs (Tart) are not wired to the relay yet: Tart's VNC server needs a password, which the relay doesn't speak. Until then, watch a macOS VM with Screen Sharing over the tailnet.

Either way, pixels go straight from the relay to the phone over the tailnet; nothing is public, and the relay accepts only tickets signed by the agent service.

## Signing an approval

On first launch the app creates a P-256 key in the Secure Enclave that needs Face ID for each use, and you copy its public key (PEM) to the server's `config/keys/`. The private key never leaves the phone.

```swift
import CryptoKit
import LocalAuthentication

let access = SecAccessControlCreateWithFlags(nil, kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
                                             [.privateKeyUsage, .biometryCurrentSet], nil)!
let key = try SecureEnclave.P256.Signing.PrivateKey(accessControl: access)   // store key.dataRepresentation in the Keychain
let publicPEM = key.publicKey.pemRepresentation

// For each approval: the server sends id, nonce and payload_sha256.
// Sign exactly these bytes: canonical JSON with sorted keys and no spaces.
let message = #"{"attachment_sha256":"\#(attachment)","decision":"approve","id":"\#(id)","nonce":"\#(nonce)","payload_sha256":"\#(payloadSha)"}"#
let signature = try key.signature(for: Data(message.utf8)).derRepresentation   // POST base64 to /v1/approvals/{id}
```

Before signing, the app recomputes `payload_sha256` from the payload it displays, so a server can't show one thing and get a signature for another.

## Releasing a login (E1.7)

1. The approval for a `login` request carries the site, exit IP and the workspace's one-time X25519 public key.
2. After Face ID, the app unlocks that single item from the Bitwarden vault on the phone (Bitwarden SDK), and builds `{"username": ..., "password": ..., "totp": ...}`.
3. It seals that JSON to the workspace key with libsodium's `crypto_box_seal` (Swift-Sodium on iOS, lazysodium on Android) and signs the decision with `attachment_sha256` = SHA-256 of the ciphertext.
4. It posts the decision, signature and base64 ciphertext. The broker can't read it; only that workspace can, once.

Banking and card sites appear only after you opt them in on the phone. Passkey-only sites always need you to take over.
