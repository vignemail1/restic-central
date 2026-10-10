# restic-central

> STATUS: PROJECT IDEA / DESIGN PHASE — NOT PRODUCTION READY.
> No operational agent, server, or interface is provided. The features described are unimplemented and unvalidated goals. Do not use this project to protect real data.

## Purpose

Design a multi-machine Restic backup orchestrator: Go agents and server, static multi-OS binaries, REST API, monitoring, and an operator web interface. Restic remains the backup engine; the central server is not the backup storage.

## Specified features

- Multiple profiles per machine, with separate include/exclude filesets.
- Backup intervals anchored to a stable timestamp, defaulting to 24 hours.
- Disabling and suspension at machine or profile level.
- Configurable pre-hooks and post-hooks, including file preparation and temporary-data cleanup.
- Backup to a primary repository followed by replication using restic copy.
- Operator-triggered local execution, with the same locking and reporting mechanisms.
- HTTPS API with individual tokens; optional mTLS; configurable certificate verification.
- Multi-channel notifications, configurable 24-hour summaries and 7-day reports.
- Web interface, support for OpenLDAP authentication, and application roles.
- Consistent local server exports, scheduled or triggered through the web interface/CLI, for backup by an external process.
- Retention target: one year of jobs for 300 machines, subject to testing.

## Documentation and reading order

The [revised specifications](docs/09-specifications-revisees.md) take precedence on the topics they modify. Documents 01 through 08 retain the initial design; conflicting provisions are superseded by this revision, particularly cron scheduling, the exclusion of hooks, independent backups, and Linux-only targeting.

1. [Revised specifications — priority document](docs/09-specifications-revisees.md)
2. [Updated decision register](docs/07-decisions.md)
3. [Initial vision](docs/01-vision-exigences.md)
4. [Initial architecture](docs/02-architecture-modele.md)
5. [Initial configuration and execution](docs/03-configuration-execution.md)
6. [API and reliability](docs/04-api-fiabilite.md)
7. [Initial security and operations](docs/05-securite-exploitation.md)
8. [Notifications and reports](docs/06-notifications-rapports.md)
9. [Initial roadmap](docs/08-roadmap-validation.md)

## Maturity

Accepted decisions are design commitments, not delivered features. Command names, fields, and endpoints remain illustrative. No test, lint, benchmark, or audit results are claimed. The license, supported versions, and distribution arrangements remain to be defined.
