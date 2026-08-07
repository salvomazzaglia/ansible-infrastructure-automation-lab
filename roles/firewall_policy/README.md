---
# Role: firewall_policy

Part of **salvomazzaglia.infrastructure_automation**.

Declarative firewall model — validate, render, optionally apply. **`aial_firewall_apply` defaults to `false`**. Molecule apply scenarios set it to `true` explicitly.

## Validation rejects

- Ports outside 1–65535
- Protocols outside tcp/udp/icmp
- RFC1918 sources
- Duplicate rule IDs
- Implicit allow-all (inbound accept + source any + no port)

Examples use documentation ranges such as `203.0.113.0/24` (TEST-NET-3).

## License

MIT

## Author

Salvatore Mazzaglia
