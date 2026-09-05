# Privacy: communicate less, protect the transport, choose the endpoint

Lambda H/2.1 is a semantic notation, not a cipher. Its normal wire contains numeric structure and semantic regions, not readable labels or literal text. That provides casual opacity; it does not encrypt meaning, authenticate a sender, or stop a host from retaining what it processes. Readable developer JSON and explicitly transferred context are distinct from the numeric wire.

The default recommendation for information that must not reach a model provider is **local inference on a controlled device, with cloud tools disabled and only necessary data supplied**. For transfer between trusted devices, wrap the packet in an established encryption tool. Do not try to invent a prompt-decodable encryption scheme.

## 1. Define who must not see what

| Observer | Useful protection | What still remains exposed |
| --- | --- | --- |
| Someone glancing at a screen | Short aliases and less displayed detail | The screen, visible response, context and recognizable patterns; this is not a security boundary. |
| Passive network observer | Authenticated encrypted transport between the actual endpoints | Endpoint identities and some traffic metadata; compromised endpoints remain a problem. |
| Storage or relay service carrying a packet | Encrypt the entire packet before upload, decrypt only at a trusted endpoint | Ciphertext length, timing, account metadata, and any unencrypted filenames or surrounding messages. |
| Hosted model provider | Keep sensitive inference local, or supply only information you are willing to disclose | Everything supplied to the hosted model, including the prompt, aliases, task structure, examples and decryption keys placed in context. |
| Another user, malware, or an administrator on the endpoint | Device security, access control, encrypted storage and careful retention | Data exposed while the authorized endpoint processes it; a notation cannot repair a compromised device. |

TLS provides channel confidentiality between endpoints, not secrecy from an endpoint. Its specification also explicitly notes that record lengths are not hidden. [1]

## 2. Opacity is not confidentiality

An observer with the bootstrap has the same public anchor definitions as the receiver. Without the bootstrap, the observer may still infer meaning from repeated patterns, known plaintext, tool use, or the agent's response. A secret vocabulary, shuffled anchors, base64, hex digits, or a request to avoid explaining the encoding is not a cryptographic guarantee.

There is an important distinction between these goals:

- A receiver can understand a packet without running a Python decoder.
- A receiver can understand plaintext after a trusted local program decrypts it.
- A remote receiver can understand a secret while its processing endpoint learns nothing about that secret.

The first is this project's usability target. The second is compatible with this project but requires genuine cryptography outside the prompt. The third is **not supplied by this implementation**. Do not claim that changing notation achieves it.

Encryption keys must never be pasted into a model prompt or uploaded with the ciphertext. If both the key and a recipe are visible to the same observer, the obscured message is not protected from that observer.

## 3. Minimize disclosure with context-local references

Use a fresh, non-identifying `context` namespace for each conversation or mission. A binding such as `X10` may identify a private object locally without placing its name in every packet. Keep the local context file outside version-controlled and synced folders when the identity must remain private.

A context file has this shape (the values below are fictional):

```json
{
  "context": "7",
  "X": {
    "X10": "private draft located on the sender's device",
    "X11": "unrelated private note"
  }
}
```

A packet may reference `X10` without copying either value. The `inspect` command reports required or missing IDs without their values. The `handoff --output NEW_DIRECTORY` command writes a numeric `packet.lh` and a separate `context.private.json` containing only referenced bindings. The new directory's parent must exist; existing destinations are not overwritten. The wire alone does not supply the text in that sidecar.

**Selective handoff is minimization, not redaction.** A required binding in the sidecar is readable disclosure to its recipient. Review both output files before sending. The numerical formatter rejects text rather than encoding it as bytes or silently dropping it. An agent cannot use a withheld identity, filename, measurement or secret merely because an alias exists; it must request the binding or solve only the abstract portion that does not need it.

For abstract advice, use intentionally non-identifying placeholders such as Party A and Party B, and keep the identity map local. Do not reuse aliases across unrelated contexts when linkability matters. The surrounding facts can still identify a person or organization even after their name is removed.

Do not copy entire chat histories, environment dumps, API credentials, unrelated files, or all context bindings into a handoff. Exact data is preserved where the task needs it; unnecessary data should not be sent.

## 4. Encrypt an actual transfer with an established tool

`age` is an external file-encryption tool with public recipients and private identity files. It is not bundled or automatically installed by encode_lang. The following is a local-terminal example, not something a model should perform with your real secret key. Check output paths first: age can overwrite an existing output file. [2]

On the intended recipient's trusted device:

```sh
umask 077
mkdir -p "$HOME/.config/encode_lang"
age-keygen -o "$HOME/.config/encode_lang/identity.txt"
age-keygen -y "$HOME/.config/encode_lang/identity.txt" > recipient.txt
```

Share only `recipient.txt`, after verifying its ownership through an authenticated channel. The sender encrypts an already-reviewed packet:

```sh
age -R recipient.txt -o outgoing.lh.age outgoing.lh
```

The recipient decrypts locally to a new output path:

```sh
age --decrypt -i "$HOME/.config/encode_lang/identity.txt" \
  -o received.lh incoming.lh.age
```

Feed the resulting plaintext only to the intended trusted receiver. Uploading `received.lh` to a hosted model discloses it at that point. The example does not configure a model, verify a recipient, erase plaintext, manage backups, or audit your device. Successful decryption is not proof of the sender's identity or authority; use an authenticated channel and inspect incoming instructions. [2][3]

The project deliberately has no home-made cipher, hand-rolled key exchange, or automatic decryption-to-action pipeline. The encrypted envelope protects transit/storage; Lambda H carries the content once decrypted.

## 5. Local inference must be local end to end

A locally installed client can still call a cloud model. Likewise, a local model can be surrounded by cloud search, browser tools, remote embeddings, file sync, logging, crash reporting, or a remote conversation interface.

For example, Ollama documents local-only operation and a cloud-disable setting:

```sh
OLLAMA_NO_CLOUD=1
```

The variable must be configured for the actual server process, followed by a restart; it is not applied simply by writing it in a document or an unrelated shell. Ollama also documents `disable_ollama_cloud` in its server configuration and a cloud-disabled log marker. This project does not alter those settings. [4]

For a strict no-egress requirement, enforce network restrictions at the host or network boundary and audit the complete application/tool chain. A `localhost` address alone does not prove that a proxy or integration avoids external processing. Protect model inputs, outputs, context maps, temporary files, backups, swap, screen recordings, and shell history according to the same threat model.

Using a remote chat interface to inspect files on a local machine does not make the inference local. Tool results sent back to that interface are part of what its processing endpoint receives.

## 6. Operational limits

The optional encode_lang codec does not execute packet actions, call model APIs, create keys, or install encryption software. Its schema/inspection output is not a security audit. Permission and sender authentication remain responsibilities of the surrounding application and the human controlling it.

Task IDs and revisions help identify snapshots; they do not provide durable replay prevention, exactly-once effects, or authentication. A receiver must compare a snapshot with its actual ledger before repeating a consequential action. A copied packet is not a reason to repeat a payment, send a message twice, or overwrite an artifact.

Do not put real secrets into the shipped examples or calibration corpus. Private context and local result files should be excluded from Git, but ignore rules are not encryption and do not remove files already tracked in history.

## Sources

Verified for this rewrite on 2026-09-05. These are external references, not dependencies of the packet or bootstrap.

1. IETF, TLS 1.3 confidentiality and metadata scope: https://www.rfc-editor.org/rfc/rfc8446.html#section-1
2. age official usage and recipient/identity documentation: https://github.com/FiloSottile/age
3. age format specification and security considerations: https://c2sp.org/age
4. Ollama official FAQ, local inference and disabling cloud features: https://docs.ollama.com/faq
