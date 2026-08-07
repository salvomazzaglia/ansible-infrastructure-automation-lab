# Threat model

## Assets

- Inventories and host/group variables
- Vault material and SSH / become credentials (operator-side)
- Playbooks and roles
- Callback reports under `reports/`
- `ansible.cfg` and CI workflow definitions
- Molecule Docker environment
- Python / Galaxy dependency graph

## Threats and mitigations

| Threat | Mitigation | Residual risk |
| --- | --- | --- |
| Accidental production targeting | Non-routable synthetic inventory; apply gate; no `ansible_host` | Private inventories can still be mis-pointed |
| Leaked inventory / credentials | Synthetic-only public data; gitignore; secrets guards | Operator may force-add secrets |
| Overly broad become | Default become false; explicit play become | Plays still escalate when intended |
| Dangerous shell patterns | Prefer modules; guards ban `curl\|bash`, `chmod 777` | Custom forks can reintroduce |
| Non-idempotent automation | Declarative modules; Molecule idempotence step | Partial check-mode gaps |
| SSH lockout | Safe defaults; validate `sshd -t`; practice on Molecule | Emergency overrides still risky |
| Firewall lockout | Apply gated off by default; rule validation | Enabling apply unsafely |
| Unsafe templating | Avoid nested Jinja in `when:`; argument specs | Complex custom vars |
| Malicious inventory variables | Prefix + specs; assert environment values | Extra-vars can override |
| Path traversal / template injection | Controlled templates; no user-upload paths in v1 | Future features need review |
| Callback secret leakage | Redaction + respect `no_log` | Mis-tagged sensitive tasks |
| Dependency / Action compromise | Pin versions; SHA-pin Actions; Dependabot | Upstream compromise possible |
| Test-container compromise | Digest pins; ephemeral destroy | Host Docker daemon trust |
| False confidence from check mode | Documented limitations | Operators may skip review |

## Out of scope for v1.0

Multi-tenant AWX/AAP threat models, cloud IAM, and production secret managers
are not claimed here.
