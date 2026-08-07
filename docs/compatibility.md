# Compatibility

Versions targeted and documented for **v1.0.0** (verified at implementation
time, August 2026):

## ansible-core

| Version | CI matrix |
| --- | --- |
| `ansible-core==2.20.7` | yes |
| `ansible-core==2.21.2` | yes |

Runtime requirement: `requires_ansible: ">=2.20.0"` (`meta/runtime.yml`).

## Python (controller)

| Version | CI matrix |
| --- | --- |
| Python 3.12 | yes |
| Python 3.13 | yes |

Development tooling declares `requires-python >= 3.11` for static tests; CI
compatibility jobs focus on 3.12/3.13 with the ansible-core pins above.

## Quality tooling

| Tool | Pin |
| --- | --- |
| ansible-lint | `26.6.0` |
| Molecule | `26.6.0` |
| molecule-plugins | `26.7.15` (with `[docker]`) |
| yamllint | `1.38.0` |
| pytest | `8.4.1` |

## Collections

| Collection | Range | Why |
| --- | --- | --- |
| `community.docker` | `>=3.12.0,<5.0.0` | Molecule create/destroy playbooks |
| `ansible.posix` | `>=1.4.0,<3.0.0` | Required by `molecule-plugins[docker]` |

Role logic prefers `ansible.builtin`.

## ansible-lint production profile

Result for v1.0.0: **PASS with two documented scoped exceptions** (not zero exclusions):

1. `var-naming[no-role-prefix]` — intentional project-wide `aial_` public prefix
2. `meta-runtime[unsupported-version]` — ansible-lint 26.6.0 catalog lists through `>=2.19.0` only; re-verified that removing the skip fails on `requires_ansible: ">=2.20.0"` even though 2.20/2.21 are the tested targets

See `docs/security-audit-v1.0.0.md`.

## Molecule image digests

| Image | Digest |
| --- | --- |
| `docker.io/library/ubuntu` | `sha256:561618e2c15bf2397621dd04f96926663a3b5616c189cf7e38db7e82f5c538ea` |
| `docker.io/library/debian` (12-slim base) | `sha256:abd67ffcfa541b485a3dff59865ab629aa048a6c613e639d36e7456b0b229241` |

Do not claim support for ansible-core, Python, or image tags outside this
matrix unless they are added to CI and this document is updated.

## Platforms (managed nodes)

Debian/Ubuntu family only in v1.0. Red Hat/Rocky and Windows are roadmap
items.
