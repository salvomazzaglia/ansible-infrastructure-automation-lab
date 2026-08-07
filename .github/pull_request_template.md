## Summary

<!-- What does this PR change and why? -->

## Safety checklist

- [ ] No real inventories, credentials, vault passwords, or SSH private keys
- [ ] Public inventory remains non-routable (`*.lab.example.invalid`, no `ansible_host`, no RFC1918)
- [ ] `aial_safe_to_apply` stays `false` for tracked synthetic inventory
- [ ] No `host_key_checking=False`, `state: latest`, `curl|bash`, `chmod 777`, or `pull_request_target`
- [ ] CI remains GitHub-hosted only; Actions pinned to full 40-character SHAs
- [ ] Role variables keep the `aial_` prefix; argument specs updated when variables change

## Test plan

- [ ] `python scripts/validate-repository.py`
- [ ] `yamllint` / `ansible-lint --profile production` (as applicable)
- [ ] `ansible-playbook --syntax-check` for touched playbooks
- [ ] `pytest`
- [ ] Molecule scenarios touched by the change (`baseline` / `orchestration`) when Docker is available
- [ ] Docs updated when behavior or safety boundaries change

## Notes

<!-- Optional: screenshots must show SYNTHETIC DEMONSTRATION DATA -->
