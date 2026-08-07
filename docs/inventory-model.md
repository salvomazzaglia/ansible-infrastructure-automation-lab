# Inventory model

## Public synthetic inventory

Path: `inventories/synthetic/`

| Control | Value |
| --- | --- |
| Hostnames | `*.lab.example.invalid` only |
| `ansible_host` | absent |
| RFC1918 | none |
| `localhost` | none |
| `aial_environment` | `synthetic` |
| `aial_safe_to_apply` | `false` |

Hosts (six):

- `ansible-bastion-01.lab.example.invalid`
- `ansible-web-01.lab.example.invalid`
- `ansible-web-02.lab.example.invalid`
- `ansible-app-01.lab.example.invalid`
- `ansible-db-01.lab.example.invalid`
- `ansible-monitor-01.lab.example.invalid`

Groups:

```text
all
├── bastion
├── web
├── application
│   └── app
├── database
└── monitoring
```

`application` contains child `app` so `group_vars/app.yml` loads while preserving
the documented application tier name.

## Variable files

- `group_vars/all.yml` — shared lab defaults and apply gate
- `group_vars/{web,app,database,monitoring}.yml` — tier overrides
- `host_vars/ansible-web-01.lab.example.invalid.yml` — host-level demo override

## Authorized / private inventories

Operators may create an **untracked** inventory (for example under
`inventories/private/`, gitignored) with:

- `aial_environment: authorized` (or `lab`)
- `aial_safe_to_apply: true` only when intentionally applying
- real connection details that must never be committed

## Molecule inventories

`molecule/*/inventory` sets `aial_environment: molecule` and
`aial_safe_to_apply: true` for disposable containers only
(`ansible_connection: docker`).

See `inventories/README.md` for operator-facing safety notes.
