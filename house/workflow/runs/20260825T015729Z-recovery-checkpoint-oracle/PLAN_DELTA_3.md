# F1 bounded closure delta 3

Authority: the user's continuation after the parked `NEEDS_REVIEW` handoff.

## Scope

Authorize only:

1. fixed-value assertions in `independent_verify.py` for all discriminator and
   security-literal fields already frozen in attempts A and B;
2. exact fixture-root directory-entry validation by name and `lstat`-equivalent
   type, rejecting every symlink and every non-regular entry;
3. two V3 verifier runs over unchanged attempts A and B;
4. three isolated temporary-copy probes: fixed discriminator mutation, extra
   directory, and expected-file symlink substitution; and
5. one final blocking council round over a frozen delta packet.

Do not alter `fixture_generator.py`, either A/B fixture tree, the V1 verifier,
production source/tests, or any operational surface. Do not access real keys,
YubiKey, Keychain, certificates, databases, network, runtime, providers,
workers, or dispatch. S1 remains unauthorized.

## Exact fixed values

V3 must require:

- fixture schema, fixture ID, `disposition=accept`, and the never-authority
  warning;
- envelope schema;
- unsigned-checkpoint schema, algorithm, and context;
- descriptor and summary schemas plus their caller-supplied source classes;
- every fixed receipt result/code/claim/non-authority/source-class literal;
- every provenance generator/label/nonce/donor/import/security/warning literal;
- disclosure schema, warning, and public test-key label;
- artifact-manifest schema, generator, frozen Python and cryptography versions,
  real-key/hardware/network security literals, and warning; and
- artifact-entry keys, hashes, and byte lengths as already required.

## Exact entry types

The fixture root itself must be a real directory, not a symlink. Its immediate
children must equal the ten frozen names. `artifact_manifest.json` and the nine
manifest-listed artifacts must each be regular files without following
symlinks. Any extra directory, file, symlink, socket, device, or other entry is
a rejection.

## Acceptance

- V3 passes unchanged attempts A and B.
- Each of the three probes is rejected for the intended reason.
- Generator and both fixture-tree hashes remain unchanged.
- Final council has no decision-bearing objection.
- Root may then accept only F1 and must still stop before S1.

No automatic remediation or additional council round is authorized if the
delta or final review fails.
