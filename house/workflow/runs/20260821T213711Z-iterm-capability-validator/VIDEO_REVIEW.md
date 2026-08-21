# Video review: `pv` / Pipe Viewer

## Evidence

- Source: <https://www.youtube.com/watch?v=gwQH-db60WU>
- Title: `This Linux command is Really Useful! pv aka Pipe Viewer`
- Channel: `You Suck at Programming`
- Uploaded: 2026-08-16
- Duration: 27:39
- Captions: automatic English; noisy evidence, not verbatim authority.
- Local evidence manifest: `youtube/gwQH-db60WU.evidence.json`.
- Primary corroboration: <https://www.ivarch.com/programs/pv.shtml> and
  <https://www.ivarch.com/programs/quickref/pv.shtml>.

## Applicable observations

1. `pv` observes a byte or line stream while passing its payload onward. This
   supports the companion's observer-only separation, but the Dream House
   should use typed app-server lifecycle events rather than infer semantic task
   progress from byte throughput.
2. Percentage and ETA require a trustworthy total. When no total exists, the
   UI must show activity/rate/status without inventing completion percentage.
3. Multiple cursor-mode instances do not have a reliable display order. The
   video recommends names, and the official manual documents `--name` for
   identifying bars. The companion should key cards by stable thread, turn,
   item, and operation identities rather than row position.
4. The video explicitly demonstrates that sleeps merely bias a race rather
   than fixing it. The companion must use sequence/predecessor checks and
   atomic state transitions, never timing delays for ordering.
5. `pv` coordinates terminal cursor writers with terminal locking, shared
   memory, and a lock-file fallback. That is useful terminal engineering but
   should not be imported here: the accepted WebView design has one renderer
   and does not write cursor-control sequences into a shared terminal.
6. At 26:58-27:17, the speaker shows Patreon display names containing ANSI
   escape characters passing through an unsanitized script. This is direct
   empirical support for the existing rule that all model, contractor, task,
   command, output, and display-name text is untrusted presentation data. The
   control-character escaping and HTML escaping already implement the needed
   boundary.

## Disposition

`NO_PLAN_BLOCKER`. Preserve the video as design evidence for structured
progress, stable identities, race-free ordering, and hostile display text. Do
not add `pv`, shared memory, terminal locks, cursor mode, or raw terminal
progress parsing to the companion. Proceed with the already-sealed pure
loopback URL/capability validator.
