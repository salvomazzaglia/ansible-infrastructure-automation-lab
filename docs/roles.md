# Roles

Collection roles under `roles/`:

| Role | Responsibility |
| --- | --- |
| `common` | Hostname (optional), timezone, locale metadata, MOTD/banner, marker dirs |
| `package_management` | Present/absent packages only (never `state: latest`) |
| `accounts` | Groups/users and authorized-key placeholders |
| `time_sync` | chrony/timesyncd preference with NTP server list |
| `logging` | Persistent journal settings; remote forward off by default |
| `ssh_hardening` | `sshd_config.d` drop-in; validates with `sshd -t` |
| `automatic_updates` | Unattended security updates policy; reboot off by default |
| `firewall_policy` | Declarative rules; render/validate; apply gated (`aial_firewall_apply`) |
| `web_service` | Minimal nginx synthetic site + rolling pool state vars |
| `service_health` | Local service/HTTP/file/config checks |

## Shared expectations

- `meta/main.yml` and `meta/argument_specs.yml` present
- Handlers reload/restart only when configuration actually changes
- FQCN modules (`ansible.builtin.*`)
- Debian/Ubuntu (`ansible_os_family == "Debian"`) asserted in preflight

## Notable safety defaults

- SSH: `PermitRootLogin` never defaults to `yes`; password auth off
- Packages: present/absent lists only
- Firewall: `aial_firewall_apply: false` in synthetic inventory
- Web: disabled in `all`, enabled in `web` group_vars
- Accounts: synthetic key placeholders are not treated as production keys

Each role has a short `README.md` with variables and examples.
