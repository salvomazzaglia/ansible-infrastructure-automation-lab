---
# Role: time_sync

Part of **salvomazzaglia.infrastructure_automation**.

Configures chrony or systemd-timesyncd using public NTP pools (`0.pool.ntp.org` style). Private NTP hosts are never hardcoded.

## Backend selection

- `aial_time_prefer: auto` — prefer chrony if installed, else timesyncd
- Force with `chrony` or `timesyncd`

## License

MIT

## Author

Salvatore Mazzaglia
