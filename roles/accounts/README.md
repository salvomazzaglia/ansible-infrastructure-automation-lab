---
# Role: accounts

Part of **salvomazzaglia.infrastructure_automation**.

Manages groups and users for the lab. No passwords. No root password changes. SSH keys are optional.

Tracked examples use `SYNTHETIC_SSH_PUBLIC_KEY_PLACEHOLDER`, which is **never** installed. Molecule can inject ephemeral real public keys via vars.

## User states

- `present` — account exists
- `absent` — account removed
- `locked` — account exists with password lock (no password is set)

## Example

```yaml
- role: salvomazzaglia.infrastructure_automation.accounts
  vars:
    aial_accounts_users:
      - name: aial_ops
        state: present
        groups: [aial_operators]
        ssh_authorized_keys:
          - "{{ molecule_ephemeral_pubkey }}"
```

## License

MIT

## Author

Salvatore Mazzaglia
