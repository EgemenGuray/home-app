# Agents tab and phone approvals (E1.6, E1.7)

The app is the only place anything risky can be approved. The approval and login flows below are identical in both setups. Only the agent service's address changes (the hub Mac with the Mac mini only, the Studio with the Mac mini + Mac Studio), and the broker stays on the hub Mac either way. The server side is in home-agents (`approvals.py`, `broker.py`, `api.py`); this is the app's half of the contract.

## Screens

- **Task board:** queued, running, waiting for you, done, failed (`GET /v1/jobs`).
- **Live view** per agent. **Mac mini only:** noVNC in a web view, served by the rented workspace VM; Linux desktops only. **Mac mini + Mac Studio:** WebRTC from the Studio, including the macOS VMs. Take over mouse and keyboard; the agent resumes with a note of what you did.
- **Pause, resume, kill.** Kill destroys the workspace and keeps the log.
- **Approvals:** a push with Approve and Deny. Shows the job, the site, the exit IP and country, and the planned action. Purchases show merchant, item and amount in CAD.
- **Audit search** over tool calls, messages, approvals, logins and takeovers.

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
