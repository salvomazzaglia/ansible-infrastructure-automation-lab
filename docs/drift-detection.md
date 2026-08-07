# Drift detection

Drift detection in this lab is **check-mode based**, not a separate CMDB or
compliance product.

## Workflow

```bash
ansible-playbook \
  --inventory inventories/synthetic/hosts.yml \
  --check --diff \
  playbooks/drift.yml
```

`playbooks/drift.yml` runs baseline and security roles (and web on the `web`
group) under check mode, then emits a per-host summary fact
(`aial_drift_summary`).

## Status vocabulary

Documented statuses for reports and samples:

| Status | Meaning |
| --- | --- |
| `compliant` | No changes reported in check mode |
| `change_required` | Check mode reported changes |
| `unavailable` | Host or facts unavailable |
| `failed` | Task failure during collection |
| `skipped` | Intentionally skipped |

Sample artifacts: `examples/sample-drift-report.json` validated by
`schemas/drift-report.schema.json`.

## Honesty bounds

- Drift signals are derived from Ansible check-mode `changed` results.
- This is **not** a vulnerability scan, CIS benchmark, or certification claim.
- Synthetic sample reports are demonstration data only.

See [check-mode.md](check-mode.md) for check-mode limitations.
