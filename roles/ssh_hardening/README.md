---
# Role: ssh_hardening

Part of **salvomazzaglia.infrastructure_automation**.

Deploys an OpenSSH `sshd_config.d` drop-in with hardened defaults. Validates with `sshd -t` before reload when `sshd` is present.

## Defaults

- `PermitRootLogin`: `prohibit-password` (never `yes`)
- `PasswordAuthentication`: no
- `PubkeyAuthentication`: yes
- `X11Forwarding`: no

## Emergency compatibility

Set `aial_ssh_emergency_compatibility: true` to apply break-glass overrides (still never `PermitRootLogin yes`).

## Handler

`Reload SSH` — reloads the `ssh` service after a successful config change.

## License

MIT

## Author

Salvatore Mazzaglia
