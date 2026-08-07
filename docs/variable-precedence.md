# Variable precedence

This lab follows Ansible’s standard precedence model. Operators should prefer
the lowest layer that achieves the desired override.

## Practical layers used here

From lower to higher influence (simplified for this repository):

1. Role defaults (`roles/*/defaults/main.yml`)
2. Inventory `group_vars/all.yml`
3. Inventory child `group_vars` (`web`, `app`, …)
4. Inventory `host_vars`
5. Play vars / role parameters in playbooks
6. Extra vars (`-e`) — highest common operator override

Argument specs validate types and choices when roles are invoked; they do not
replace precedence rules.

## Project conventions

- Public variables are prefixed with `aial_`.
- Defaults are lab-safe (for example firewall apply off, web disabled
  fleet-wide until the `web` group enables it).
- Synthetic inventory never sets become passwords or vault secrets.
- Placeholder SSH authorized keys use
  `SYNTHETIC_SSH_PUBLIC_KEY_PLACEHOLDER` and are not installed as real keys by
  the accounts role when placeholders are detected (see role tasks).

## Avoid

- Encoding secrets in `group_vars` committed to git
- Overriding `aial_safe_to_apply` to `true` in tracked synthetic inventory
- Using nested Jinja expressions inside `when:` conditions

For inventory structure see [inventory-model.md](inventory-model.md).
For role inputs see [roles.md](roles.md).
