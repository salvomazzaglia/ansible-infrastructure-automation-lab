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
| molecule-plugins | `23.7.0` (with `[docker]`) |
| yamllint | `1.37.1` |
| pytest | `8.4.1` |

## Collections

| Collection | Range |
| --- | --- |
| `community.docker` | `>=3.12.0,<5.0.0` |

Used for Molecule create/destroy. Role logic prefers `ansible.builtin`.

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
