# Release notes — v1.0.0

**Date:** 2026-08-07  
**Collection:** `salvomazzaglia.infrastructure_automation` `1.0.0`

## Highlights

- Portfolio-ready Ansible infrastructure automation laboratory with ten roles,
  multi-tier synthetic inventory, and fail-closed apply gates
- Check-mode and drift playbooks, rolling web orchestration (`serial: 1`),
  and sanitized `automation_report` callback
- Molecule scenarios `baseline` and `orchestration` using digest-pinned
  ephemeral containers
- Static quality stack: yamllint, ansible-lint production profile, pytest
  repository guards, collection build

## Compatibility targets

- ansible-core **2.20.7** and **2.21.2**
- Python **3.12** and **3.13** (CI matrix)
- ansible-lint **26.6.0**, Molecule **26.6.0**

## Quality gates for this release

v1.0.0 is designed to pass the following gates:

- yamllint
- ansible-lint `--profile production`
- ansible-playbook `--syntax-check` for all lab playbooks
- `scripts/validate-repository.py` / pytest guards
- `ansible-galaxy collection build`
- Molecule converge → idempotence → verify for `baseline` and `orchestration`
  (scenarios provided; executed on GitHub-hosted CI runners with Docker)

Do not treat documentation alone as proof that Molecule has been run on a
given workstation.

## Known limitations

- Debian/Ubuntu managed nodes only
- Public inventory is non-routable and not an apply target
- No real load balancer, AWX/AAP, cloud inventory, or Galaxy publish
- Check mode is advisory and not a safety guarantee for apply

## Upgrade notes

Initial release — no upgrade path.
