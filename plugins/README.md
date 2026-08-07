# Plugins

Collection plugins for `salvomazzaglia.infrastructure_automation`.

## Callback: `automation_report`

FQCN: `salvomazzaglia.infrastructure_automation.automation_report`

Aggregate callback that writes **sanitized** JSON execution metadata (play, host
alias, task, role, status flags, duration, and recap). It never stores raw
secrets, vault values, passwords, SSH key material, or `no_log` task payloads.

Enable:

```ini
[defaults]
callbacks_enabled = salvomazzaglia.infrastructure_automation.automation_report
```

Report directory (default `reports/`, gitignored):

- Environment: `AIAL_REPORT_DIR`
- Ini: `[callback_automation_report] report_dir=...`
