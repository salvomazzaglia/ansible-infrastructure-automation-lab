# Rolling deployment

## Pattern

Web updates use Ansible `serial: 1` so one host is processed at a time
(`playbooks/web.yml` and the web play in `site.yml`).

Per-host workflow:

1. Preflight gates
2. Simulate remove from synthetic load-balancer pool (`draining`)
3. Apply `web_service`
4. Run `service_health`
5. Simulate restore to pool (`in_service`)

Pool member states are variables only:

- `in_service`
- `draining`
- `out_of_service`

## What is not included

There is **no real load balancer**. Pool transitions are synthetic
orchestration state recorded via `set_fact` / `debug` for teaching serial
batches and health gating.

Roadmap may add real LB adapters later; v1.0 does not.
