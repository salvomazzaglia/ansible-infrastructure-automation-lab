# Safety model

## Goals

Fail closed when an operator might accidentally mutate real infrastructure
using this public repository.

## Controls

| Control | Behavior |
| --- | --- |
| Synthetic hostnames | `*.lab.example.invalid` only |
| No `ansible_host` | Public inventory cannot resolve to real IPs via inventory |
| `aial_safe_to_apply: false` | Apply asserts fail outside check mode |
| `aial_environment` allow-list | `synthetic` \| `lab` \| `authorized` \| `molecule` |
| Localhost rejection | Blocked unless `aial_environment=molecule` |
| `host_key_checking` | Remains `True` in `ansible.cfg` and CI |
| `become` default | `False` in `ansible.cfg`; playbooks opt in explicitly |
| Firewall apply | Off in synthetic inventory |
| Secrets | Placeholders only; vault example unencrypted placeholders |
| CI | No secrets, no deploy, GitHub-hosted only |

## Check vs apply

- Check mode may run against synthetic inventory.
- Apply against synthetic inventory is refused by preflight and by
  `scripts/check-lab.sh --apply`.
- Apply is intended for Molecule ephemeral containers or an untracked
  authorized inventory.

## Residual risk

Misconfigured private inventories, overly broad become, or disabling guards
locally can still cause harm. The lab reduces accidental risk; it does not
replace operator judgment.
