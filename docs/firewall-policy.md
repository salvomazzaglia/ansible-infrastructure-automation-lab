# Firewall policy

Role: `roles/firewall_policy`

## Model

Declarative inbound/outbound rules are validated and rendered. Applying
firewall changes is **opt-in**:

- Synthetic inventory: `aial_firewall_apply: false`
- Molecule may enable apply explicitly when testing enforcement on ephemeral
  containers

## Validation rejects

- Ports outside 1–65535
- Protocols outside tcp/udp/icmp
- RFC1918 sources in rule data
- Duplicate rule IDs
- Implicit allow-all (inbound accept + source any + no port)

Examples use documentation ranges such as `203.0.113.0/24` (TEST-NET-3).

## Lockout awareness

Enabling `aial_firewall_apply: true` with an incomplete SSH allow rule can
interrupt management access on real hosts. Keep apply disabled until rules are
reviewed in check mode against an authorized inventory or Molecule target.
