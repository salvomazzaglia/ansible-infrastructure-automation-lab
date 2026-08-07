---
# Inventories

This directory holds **synthetic** Ansible inventories for the
Ansible Infrastructure Automation Lab.

## Safety model

Public inventories under `inventories/synthetic/` are **documentation and
planning data**, not deployment targets.

| Control | Synthetic inventory value |
| --- | --- |
| `aial_environment` | `synthetic` |
| `aial_safe_to_apply` | `false` |
| Hostnames | `*.lab.example.invalid` only |
| `ansible_host` | **absent** (deliberately) |
| RFC1918 addresses | **none** |
| `localhost` / local connection | **none** |

### Why apply is blocked

Playbook preflight (`playbooks/tasks/preflight.yml`) requires
`aial_safe_to_apply: true` for any non-check-mode run. The tracked synthetic
inventory keeps this `false`, so accidental `ansible-playbook` apply against
public hosts fails closed.

Check mode may proceed with `aial_safe_to_apply: false`:

```bash
ansible-playbook \
  --inventory inventories/synthetic/hosts.yml \
  --check --diff \
  playbooks/check.yml
```

### Non-routable by design

Hostnames use the reserved `example.invalid` TLD. There are no routable
`ansible_host` values, so the inventory cannot accidentally open SSH sessions
to real infrastructure from a default control node.

### Authorized / private inventories

Operators may create an **untracked** private inventory (for example under
`inventories/private/`, which is gitignored) with:

- `aial_environment: authorized` (or `lab` / `molecule`)
- `aial_safe_to_apply: true` only when intentionally applying
- real connection details never committed to this repository

Do **not** ship a production inventory in this project.

### Molecule

Ephemeral Molecule scenarios under `molecule/baseline/` and
`molecule/orchestration/` set `aial_environment: molecule` and
`aial_safe_to_apply: true` against disposable Docker containers only
(digest-pinned images, `ansible_connection: docker`, no real SSH hosts).

```bash
./scripts/run-molecule.sh              # both scenarios
./scripts/run-molecule.sh baseline      # one scenario
./scripts/check-lab.sh                  # --check --diff vs Molecule inventory
```

## Layout

```text
inventories/
├── README.md                 # this file
└── synthetic/
    ├── hosts.yml             # six fictional hosts, five groups
    ├── group_vars/
    │   ├── all.yml
    │   ├── web.yml
    │   ├── app.yml
    │   ├── database.yml
    │   └── monitoring.yml
    └── host_vars/
        └── ansible-web-01.lab.example.invalid.yml
```

## Groups

```text
all
├── bastion
├── web
├── application
│   └── app
├── database
└── monitoring
```

The `application` group contains child group `app` so `group_vars/app.yml`
loads while preserving the documented `application` tier name.
