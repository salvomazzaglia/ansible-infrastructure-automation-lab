# Molecule testing

## Scenarios

| Scenario | Purpose |
| --- | --- |
| `baseline` | Converge common baseline + security-related roles; idempotence; verify |
| `orchestration` | Two web targets; serial web deployment; handlers; health; pool simulation |

Both use Molecule **26.x ansible-native** configuration with
`create.yml` / `destroy.yml` driven by `community.docker`.

## Images (digest-pinned)

Never `:latest`.

| Image | Digest |
| --- | --- |
| Ubuntu (platform) | `docker.io/library/ubuntu@sha256:561618e2c15bf2397621dd04f96926663a3b5616c189cf7e38db7e82f5c538ea` |
| Debian 12 slim base | `docker.io/library/debian@sha256:abd67ffcfa541b485a3dff59865ab629aa048a6c613e639d36e7456b0b229241` |

Baseline builds a local systemd-capable image `FROM` the Debian slim digest
(`molecule/baseline/Dockerfile.debian12`).

## Safety

- `aial_environment: molecule`
- `aial_safe_to_apply: true` (ephemeral only)
- `ansible_connection: docker` — no real SSH hosts
- Firewall remains render-oriented unless a scenario explicitly enables apply

## Running locally

```bash
./scripts/run-molecule.sh              # both
./scripts/run-molecule.sh baseline
./scripts/run-molecule.sh orchestration
```

Requires Docker and dependencies from `requirements-dev.txt` plus
`molecule-plugins[docker]`.

## CI expectation

Molecule scenarios are provided and are **expected to run in CI** on
GitHub-hosted Ubuntu runners with Docker. Do not claim a local Molecule pass
unless you have actually run the scenarios in that environment.
