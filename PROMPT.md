# Start a Lambda H/2 conversation

Paste the complete contents of [`prompt/BOOTSTRAP.md`](prompt/BOOTSTRAP.md) into the receiving AI session. It is self-contained; the receiver does not need Python or repository access.

A bare `ΛH2|` packet requests the represented response directly. `ENCODE:` requests a packet; `DECODE:` requests an explanation rather than execution. When the bootstrap includes a task, the agent should address it immediately instead of returning a readiness-only response.

This file is a pointer, not another protocol definition. The v1 bootstrap is historical material under `archive/v1/`, not the current language. Encoding is not encryption; see [`docs/PRIVACY.md`](docs/PRIVACY.md).
