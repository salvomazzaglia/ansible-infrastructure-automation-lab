# Secrets and Ansible Vault

## What this repository contains

- `examples/vault.example.yml` — placeholder values
  (`CHANGE_ME_WITH_ANSIBLE_VAULT`) only
- No encrypted vault files with real secrets
- No vault password files
- No private keys

`.gitignore` excludes vault password patterns, `reports/`, and private
inventory paths.

## Recommended operator pattern

1. Keep secrets out of git.
2. Encrypt strings or files with `ansible-vault` locally.
3. Provide the vault password via a local mechanism (prompt, agent, or
   CI-backed secret store in a private fork — not used by this public CI).
4. Prefer `no_log: true` on tasks that touch credentials.

## Callback protection

The `automation_report` callback redacts sensitive keys and never stores
`no_log` payloads. See `plugins/README.md`.

## Explicit non-goals for v1.0

HashiCorp Vault, cloud secret managers, and OIDC-backed secret injection are
roadmap items only and are not implemented.
