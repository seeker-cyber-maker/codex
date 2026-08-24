# Private Backup Receipt

Observed at `2026-08-24T22:47:01Z`:

- source commit: `6685bacb31` (`house: add sealed synthetic recovery ledger`)
- seal/evidence commit: `95cf5e4ceff22ace3f94babbed823e95d842eb4c`
- private remote: `git@github.com:seeker-cyber-maker/codex-dream-house.git`
- branch: `codex/dream-house-auto-switcher`
- `git ls-remote` reproduced
  `95cf5e4ceff22ace3f94babbed823e95d842eb4c` after the push.

This receipt records off-site presence of the sealed source and evidence
commits. The receipt's own later commit is verified separately at handoff; it
does not alter the sealed source hashes.
