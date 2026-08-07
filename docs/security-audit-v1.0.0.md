# Security audit — v1.0.0

**Auditor role:** repository authoring / release checklist  
**Date:** 2026-08-07  
**Scope:** tracked files in `ansible-infrastructure-automation-lab` v1.0.0

## Checks performed

Automated and manual review covered:

- Real IPs / RFC1918 literals in inventories, examples, playbooks, roles
- Real domains/hostnames outside `.example.invalid` lab names
- Personal paths, Gmail addresses, cloud keys, GitHub tokens
- SSH private keys / `BEGIN PRIVATE KEY` / vault password files
- Real SSH public keys vs synthetic placeholders
- `ansible_host` presence; `/etc/ansible/hosts` usage
- `host_key_checking=False`
- `curl|bash` / `wget|bash` / `chmod 777` / `state: latest`
- `ignore_errors` abuse, `changed_when: false` without justification
- `no_log` handling in callback plugin
- CI: self-hosted, `pull_request_target`, unpinned Actions
- Inventory apply gate (`aial_safe_to_apply: false`)

Primary automation: `scripts/validate-repository.py` and pytest suites under
`tests/`.

## Findings

| Area | Result |
| --- | --- |
| Synthetic inventory hygiene | Pass — six `.lab.example.invalid` hosts; no `ansible_host` |
| Secrets / keys in git | Pass — placeholders only (`CHANGE_ME_WITH_ANSIBLE_VAULT`, synthetic key marker) |
| Dangerous shell patterns | Pass — guards enforce absence |
| Package `state: latest` | Pass — forbidden |
| SSH defaults | Pass — no `PermitRootLogin yes` default |
| ansible.cfg host key checking | Pass — remains enabled |
| Callback redaction contract | Pass — `REDACTED` / `no_log` / `AIAL_REPORT_DIR` present |
| CI soft-guards | Pass design — GitHub-hosted, SHA-pinned Actions, no `pull_request_target` |

## Corrections during development

Issues discovered during authoring were fixed before release tagging (FQCN
preference, inventory safety vars, firewall apply default, Molecule digests,
callback sanitization, Ubuntu Molecule images built FROM pinned digests with
systemd). Re-run `validate-repository.py` after any future edit.

## ansible-lint exclusions (narrow)

`.ansible-lint` uses profile `production` with **two intentional scoped skips**
(this is **not** a zero-exclusion result):

| Skip | Scope | Re-verified 2026-08-07 | Reason |
| --- | --- | --- | --- |
| `var-naming[no-role-prefix]` | global skip_list entry only for this rule id | Yes — public API uses `aial_*` across roles | Argument specs still enforce types/choices; other var-naming checks remain active |
| `meta-runtime[unsupported-version]` | global skip_list entry only for this rule id | Yes — removing it fails: linter catalog lists `>=2.15.0`…`>=2.19.0` only | `meta/runtime.yml` correctly requires `>=2.20.0`; project tested on 2.20.7 and 2.21.2 |

No skips for: syntax-check, fqcn, package-latest, risky-shell-pipe,
command-instead-of-module, no-changed-when, no-handler, or risky-file-permissions.

## Accepted false positives / documentation mentions

- Docs and comments may mention forbidden patterns while explaining why they
  are banned.
- TEST-NET documentation ranges (for example `203.0.113.0/24`) appear in
  synthetic firewall examples — not RFC1918.
- Callback plugin header references GPL-compatible Ansible plugin licensing
  text while the project license remains MIT for the laboratory distribution.

## Remaining limitations

- Operators can still create unsafe private inventories locally.
- Check mode can create false confidence (documented).
- Molecule depends on a trusted local/CI Docker daemon.
- Upstream Action or dependency compromise remains a residual supply-chain
  risk despite pinning.

## Conclusion

For v1.0.0 public content, the repository meets the synthetic-lab safety bar:
no real production inventory, no committed credentials, fail-closed apply on
public examples, and CI without secrets or deploy privileges.
