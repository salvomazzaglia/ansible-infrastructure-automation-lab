# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | yes       |

## Vulnerability classes of interest

- Accidental production targeting / inventory leakage
- Credential or vault material committed to the repository
- Callback report secret leakage
- Unsafe shell pipelines or privilege escalation patterns in roles
- CI supply-chain issues (unpinned Actions, self-hosted runners, `pull_request_target`)
- Preflight bypass that allows apply against synthetic public inventory
- SSH or firewall lockout patterns in hardening roles

## Reporting

Please use **GitHub Private Vulnerability Reporting** on this repository.

Do not include real inventories, vault passwords, SSH private keys, become passwords, or cloud credentials in reports.

## Scope notes for v1.0

Version 1.0 is a synthetic laboratory. Public inventories are intentionally non-routable and apply is gated. Reports about "missing production integrations" (AWX, AAP, cloud inventory, real load balancers) are out of scope for 1.0; reports involving accidental apply paths, secret leakage, or CI hardening regressions are in scope.
