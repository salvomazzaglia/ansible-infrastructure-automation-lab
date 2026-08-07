# Continuous integration

Workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)

## Security posture

- GitHub-hosted runners only (`ubuntu-latest`)
- `permissions: contents: read`
- No `pull_request_target`
- No self-hosted runners
- No repository secrets required
- No deploy / Galaxy publish job
- Actions pinned to full 40-character commit SHAs

Pinned actions:

| Action | SHA | Tag |
| --- | --- | --- |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | v7.0.1 |
| `actions/setup-python` | `5fda3b95a4ea91299a34e894583c3862153e4b97` | v7.0.0 |
| `actions/upload-artifact` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | v7.0.1 |

## Jobs

1. **lint** — yamllint, ansible-lint production profile, playbook syntax checks,
   `scripts/validate-repository.py`
2. **core-compatibility** — matrix `ansible-core==2.20.7` and `2.21.2` ×
   Python 3.12 and 3.13; deps install; collection build; syntax; pytest
3. **molecule** — Ubuntu only; `molecule test` for `baseline` and
   `orchestration` with `molecule-plugins[docker]` and `community.docker`
4. **package** — `ansible-galaxy collection build` and upload `.tar.gz` artifact

## Dependabot

`.github/dependabot.yml` updates **pip** and **github-actions** weekly.

## Local mirror

```bash
python scripts/run-ci.py
```

Runs static checks without touching real infrastructure. Molecule remains
separate via `scripts/run-molecule.sh`.
