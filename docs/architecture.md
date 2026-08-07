# Architecture

This laboratory ships as the Ansible collection
`salvomazzaglia.infrastructure_automation` (version **1.0.0**). It demonstrates
safe configuration management for Debian/Ubuntu hosts using synthetic
inventories, reusable roles, check mode, drift collection, and Molecule
ephemeral testing.

## Layers

```text
Control node (developer / CI)
  ├── ansible.cfg (host_key_checking=True, become=False by default)
  ├── Collection roles + playbooks + callback plugin
  ├── Synthetic inventory (planning / check-only)
  ├── Private inventory (untracked, operator-owned)
  └── Molecule inventories (ephemeral Docker only)
```

## Control flow

1. Operator selects an inventory and playbook explicitly.
2. Shared `playbooks/tasks/preflight.yml` asserts environment and apply gates.
3. Roles apply desired state using `ansible.builtin` modules and handlers.
4. Optional `automation_report` callback writes sanitized JSON metadata.
5. Molecule scenarios create disposable containers, converge, assert
   idempotence, verify, then destroy.

## Playbook map

| Playbook | Purpose |
| --- | --- |
| `site.yml` | Full desired state + rolling web tier |
| `baseline.yml` | Common baseline roles |
| `security.yml` | SSH, automatic updates, firewall policy |
| `web.yml` | Serial web rolling with synthetic LB pool state |
| `check.yml` | Check-mode preview (`check_mode` / `diff` reinforced) |
| `drift.yml` | Check-mode drift collection |
| `health.yml` | Local service health verification |

## Safety boundaries

- Public inventory hosts use `*.lab.example.invalid` and omit `ansible_host`.
- Tracked inventory sets `aial_safe_to_apply: false`.
- Apply is refused unless check mode or an authorized inventory sets the gate.
- Molecule uses `ansible_connection: docker` against digest-pinned images.

See also: [safety-model.md](safety-model.md), [collection-design.md](collection-design.md),
[inventory-model.md](inventory-model.md).
