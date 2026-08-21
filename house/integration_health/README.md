# Integration health gate

`house.integration_health` evaluates a trusted, versioned desired-state
contract against a declared filesystem root. It is deliberately read-only:
there is no repair operation, shell execution, watcher, provider call, terminal
registration, or dispatch path.

Each artifact names a safe relative path, optional SHA-256, executable
requirement, and optional scalar JSON-pointer expectations. `HEALTHY` means
every check matched. `REPAIR_REQUIRED` reports stable defect codes while making
clear that repair needs a separate explicit operation.

The first target is a future iTerm companion binding, but the same narrow
contract can verify provider hooks, model-cache path wiring, or local adapters
when a trusted caller supplies the expected state.

It treats an invalid contract as a hard error and observed drift as a report:

```python
from house.integration_health import evaluate_integration_health

report = evaluate_integration_health(contract, root="/trusted/integration/root")
assert report["state"] in {"HEALTHY", "REPAIR_REQUIRED"}
```

No health result grants repair authority.
