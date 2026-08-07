---
# Role: common

Part of **salvomazzaglia.infrastructure_automation**.

Baseline host policy for the Ansible Infrastructure Automation Lab: optional hostname, timezone (default UTC), locale metadata, standard directories, MOTD/banner, and a config marker.

## Requirements

- ansible-core >= 2.20
- Debian / Ubuntu family with `timedatectl` available

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `aial_common_manage_hostname` | `false` | Apply hostname change |
| `aial_common_hostname` | `""` | Synthetic hostname when managed |
| `aial_common_timezone` | `UTC` | IANA timezone |
| `aial_common_locale` | `en_US.UTF-8` | Documented locale metadata |
| `aial_common_standard_dirs` | lab paths under `/opt/aial` | Directories to create |
| `aial_common_manage_motd` | `true` | Manage `/etc/motd` |
| `aial_common_manage_banner` | `true` | Manage `/etc/issue.net` |

## Example Playbook

```yaml
- hosts: lab_web
  roles:
    - role: salvomazzaglia.infrastructure_automation.common
      vars:
        aial_common_manage_hostname: true
        aial_common_hostname: web-01.lab.example.invalid
```

## License

MIT

## Author

Salvatore Mazzaglia
