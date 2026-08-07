# Development plan

Implementation followed the laboratory development order below. Phases are
summarized for maintainers; detailed role/playbook work lives in the
repository tree.

## Phases

| Phase | Focus |
| --- | --- |
| 1 | Inspect directory; capture this plan |
| 2 | Verify ansible-core, Python, ansible-lint, Molecule versions |
| 3 | Collection structure and `galaxy.yml` / `meta/runtime.yml` |
| 4 | Synthetic inventory and safety variables |
| 5 | Preflight safety tasks |
| 6–15 | Implement ten roles (`common` … `service_health`) |
| 16 | Role argument specs |
| 17–18 | Playbooks and rolling web orchestration |
| 19–20 | Callback plugin; check/drift reporting |
| 21–22 | Sample reports and screenshot |
| 23–24 | Molecule `baseline` and `orchestration` |
| 25 | pytest repository tests (≥150 cases) |
| 26–28 | yamllint, ansible-lint production profile, syntax checks |
| 29–30 | Molecule quality gates (expected in CI); collection build |
| 31 | GitHub Actions with verified SHA pins |
| 32 | Documentation under `docs/` and root README |
| 33–35 | Security/privacy audit; fixes; re-run quality gates |
| 36 | Git initialization / staged-file inspection (operator) |

## Current status notes

- Collection layout, roles, playbooks, inventories, tests, and Molecule
  scenarios are present in-tree.
- Static gates are exercised locally via `scripts/run-ci.py` and in CI lint /
  core-compatibility jobs.
- Molecule scenarios are provided and expected to run in the CI `molecule`
  job on GitHub-hosted Ubuntu runners; local Molecule success should only be
  claimed after an actual run with Docker.
