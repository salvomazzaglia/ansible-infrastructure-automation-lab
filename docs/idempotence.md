# Idempotence

Idempotence means a second converge against the same desired state reports
**no changes** (or only documented exceptions).

## How this lab enforces it

- Roles use declarative modules (`package`, `template`, `copy`, `file`,
  `user`, `group`, `service`) instead of unconditional shell mutation.
- Templates are stable (no `random` filters in Jinja templates).
- `changed_when: false` is allowed only for read-only probes with an explicit
  justification comment (repository guards scan for abuse).
- `state: latest` is forbidden by repository guards.
- Molecule scenarios include an **idempotence** step after converge for both
  `baseline` and `orchestration`.

## Operator workflow

1. Converge once (Molecule or authorized inventory).
2. Converge again — expect zero changes.
3. If changes remain, inspect the task list; do not silence with blanket
   `changed_when: false`.

## Limits

Handlers that restart services still fire when templates change. That is
desired. Idempotence claims apply to configuration convergence, not to
external package repository churn outside the present/absent model.
