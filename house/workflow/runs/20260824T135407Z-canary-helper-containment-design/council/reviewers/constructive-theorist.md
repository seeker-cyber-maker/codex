# Design review: constructive-theorist

Packet SHA-256: 99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819  
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass  
Reviewer self-report: constructive-theorist  
Harness: provider-orchestration ClinePass OpenAI shim  
System-prompt profile: council role only; otherwise unknown  
Memory: unknown  
Reasoning mode: unknown  
Disposition: completed  

## Proposed boundary

Recommend **ACCEPT_DESIGN_ONLY** for the generated-canary helper containment design v1. The minimum implementable architecture is:

- A sealed, signed parent binary (App Sandbox + hardened runtime, no exceptions) that embeds and verifies the exact helper binary.
- A sealed helper binary (inherited sandbox, hardened runtime, `get-task-allow` absent) that inherits exactly FDs 3–6, no others.
- A generated test coordinator that creates all channels with `O_CLOEXEC`, launches the parent via `posix_spawn` with `POSIX_SPAWN_CLOEXEC_DEFAULT | POSIX_SPAWN_SETSID`, verifies signatures and hashes, and never touches real secrets, Keychain, or network.
- A controller SQLite ledger that provides a durable, monotonic sink‑attempt gate (`synchronous=FULL`, fullfsync, separate‑read verification) before the one‑use `RELEASE_ONCE` frame.
- An in‑process memory‑only mock sink and a sterile observer that scans declared surfaces for canary material.

The trusted computing base consists of:  
1. The signed parent and helper binaries (identity verified by coordinator via static hashes and Apple code‑signing inspection).  
2. The coordinator harness (test code, no ambient authority).  
3. The controller SQLite store with `fs
