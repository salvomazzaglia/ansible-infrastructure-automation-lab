# Changelog

All notable changes to this project are documented in this file.

## 1.0.0 — 2026-08-07

Initial public release of the Ansible Infrastructure Automation Lab
(`salvomazzaglia.infrastructure_automation` collection):

- Ten reusable roles with argument specs and `aial_` variable prefix
- Synthetic multi-tier inventory (`bastion`, `web`, `app`, `database`, `monitoring`)
- Playbooks for site, baseline, security, web rolling, check, drift, and health
- Preflight gates (`aial_environment`, `aial_safe_to_apply`) fail closed on apply
- Check-mode workflows, drift collection vocabulary, and sanitized callback reports
- Molecule scenarios `baseline` and `orchestration` (ephemeral Docker, digest-pinned images)
- Static quality gates: yamllint, ansible-lint production profile, pytest, repository guards
- CI on GitHub-hosted runners with SHA-pinned Actions (no secrets, no deploy)
