# Collection design

## Identity

| Field | Value |
| --- | --- |
| Namespace | `salvomazzaglia` |
| Name | `infrastructure_automation` |
| Version | `1.0.0` |
| Runtime | `requires_ansible: ">=2.20.0"` |
| License | MIT |

Metadata lives in `galaxy.yml` and `meta/runtime.yml`. The repository is the
collection root so roles, plugins, and playbooks are co-located for learning
and CI.

## Layout

```text
galaxy.yml
meta/runtime.yml
roles/                 # ten laboratory roles
playbooks/             # site, baseline, security, web, check, drift, health
plugins/callback/      # automation_report
inventories/synthetic/ # non-routable planning inventory
molecule/              # baseline + orchestration scenarios
tests/                 # pytest repository guards
scripts/               # validate-repository, run-ci, molecule helpers
```

## Design principles

- Prefer `ansible.builtin` over external collections for role logic.
- External collection dependency is minimal: `community.docker` for Molecule
  create/destroy (see `requirements.yml`).
- All public role variables use the `aial_` prefix.
- Every role ships `meta/argument_specs.yml`.
- Templates avoid nested Jinja in condition expressions and use explicit
  booleans compatible with ansible-core 2.19+ templating trust behavior.
- Collection build excludes tests, Molecule, docs, inventories, and scripts
  via `galaxy.yml` `build_ignore`.

## Distribution

`ansible-galaxy collection build` produces
`salvomazzaglia-infrastructure_automation-1.0.0.tar.gz`. CI uploads the artifact
for inspection and does **not** publish to Ansible Galaxy.
