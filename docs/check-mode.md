# Check mode

Check mode (`--check`) asks Ansible to report what would change without
applying mutations for modules that support it.

## Lab usage

```bash
ansible-playbook \
  --inventory inventories/synthetic/hosts.yml \
  --check --diff \
  playbooks/check.yml
```

`playbooks/check.yml` also sets play-level `check_mode: true` and `diff: true`.
Preflight **allows** check mode when `aial_safe_to_apply` is `false`.

Helper script (defaults to Molecule inventory when present):

```bash
./scripts/check-lab.sh --check
```

## Supported intents

- Preview baseline and security role impact
- Collect drift signals (`playbooks/drift.yml`)
- Teach operators to read `--diff` output before apply

## Important limitation

> Check mode can reduce deployment risk but does not guarantee that an apply
> operation will be safe or produce exactly the same result.

Some modules have partial check-mode support. Handlers may not run the same
way. External side effects (package indexes, remote APIs) can still differ.
Always treat check mode as advisory, then apply only against Molecule or an
authorized private inventory.
