# Contributing

Thank you for contributing to **ansible-infrastructure-automation-lab**.

## Rules

1. Keep all public inventories and examples **synthetic**.
2. Use `*.lab.example.invalid` hostnames; do not add `ansible_host`, RFC1918, or localhost to public inventories.
3. Keep `aial_safe_to_apply: false` for tracked synthetic inventory.
4. Prefer `ansible.builtin` FQCN modules; avoid `state: latest`, `curl|bash`, `chmod 777`, and disabling host key checking.
5. Do not commit vault passwords, private keys, or real credentials.
6. CI must remain GitHub-hosted only with Actions pinned to full 40-character SHAs.
7. Document safety limitations honestly — especially check mode vs apply.

## Local development

```bash
python -m pip install -r requirements-dev.txt
ansible-galaxy collection install -r requirements.yml
python scripts/validate-repository.py
python scripts/run-ci.py
python -m pytest
```

Molecule (Docker required):

```bash
./scripts/run-molecule.sh
# or
./scripts/run-molecule.sh baseline
```

Safe check-mode helper:

```bash
./scripts/check-lab.sh --check
```

## Pull requests

Use the repository PR template. Describe synthetic-only test evidence. Do not paste real host data into issues or PRs.
