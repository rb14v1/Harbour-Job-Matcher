# Database restore runbook

Server: `psql-job-matcher` (Azure Database for PostgreSQL Flexible Server).

## Backup configuration
- Automated backups, 30-day retention (`backup_retention_days = 30`).
- Point-in-time recovery (PITR) is available for the whole retention window.
- Geo-redundant backup storage replicates backups to the paired region.

## Point-in-time restore
1. `az postgres flexible-server restore --resource-group <rg> --name psql-job-matcher-restore --source-server psql-job-matcher --restore-time <UTC ISO timestamp>`
2. Verify data (row counts, pgvector extension present).
3. Point the backend's `POSTGRES_HOST` to the restored server.

## Geo-restore (primary region outage)
1. `az postgres flexible-server geo-restore --resource-group <rg> --name psql-job-matcher-geo --source-server psql-job-matcher --location <paired region>`
2. Verify and repoint the backend as above.

## Pre-go-live test
Perform a PITR restore and a geo-restore to temporary servers, verify data, record the result below, then delete the temporary servers.

| Date | Type | Result | Operator |
|------|------|--------|----------|
|      |      |        |          |
