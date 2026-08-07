---
# Role: package_management

Part of **salvomazzaglia.infrastructure_automation**.

Declarative apt package management for Debian/Ubuntu. Installs a baseline list with `state: present` only — never `latest` by default.

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `aial_packages_present` | ca-certificates, curl, gnupg, vim-tiny | Ensure present |
| `aial_packages_absent` | `[]` | Ensure absent |
| `aial_packages_update_cache` | `true` | Update apt cache |
| `aial_packages_cache_valid_time` | `3600` | Cache validity seconds |
| `aial_packages_held` | `[]` | Optional dpkg holds |

## Example

```yaml
- role: salvomazzaglia.infrastructure_automation.package_management
  vars:
    aial_packages_present:
      - nginx
      - curl
    aial_packages_absent:
      - popularity-contest
```

## License

MIT

## Author

Salvatore Mazzaglia
