# SSH hardening

Role: `roles/ssh_hardening`

## Defaults (lab-safe)

| Setting | Default |
| --- | --- |
| `PermitRootLogin` | `prohibit-password` (never `yes` as default) |
| `PasswordAuthentication` | `no` |
| `PubkeyAuthentication` | `yes` |
| `X11Forwarding` | `no` |

Configuration is deployed as an `sshd_config.d` drop-in and validated with
`sshd -t` before reload when `sshd` is present. Handler: **Reload SSH**.

## Emergency compatibility

`aial_ssh_emergency_compatibility: true` enables break-glass overrides for lab
recovery scenarios. Even then, `PermitRootLogin yes` is not used as a secure
default path.

## Lockout awareness

Hardening can lock operators out if keys are wrong. Practice on Molecule
containers first. Public synthetic inventory cannot open real SSH sessions
because hosts are non-routable and lack `ansible_host`.

Repository guards fail if defaults regress to insecure SSH settings.
