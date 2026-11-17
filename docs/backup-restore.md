# Database backup and restore runbook

Server: Azure Database for PostgreSQL Flexible Server `psql-job-matcher` (resource group `job-matcher`), defined in `infra/main.tf`.

## Configuration
- Automated backups: enabled, retention 35 days (minimum required: 30).
- Geo-redundant backup: enabled (backups are replicated to the paired Azure region).
- Point-in-time recovery (PITR): available at any point within the retention window.

## Restore procedure (PITR)
1. Choose the target timestamp (UTC) within the retention window.
2. Run:
   `az postgres flexible-server restore --resource-group job-matcher --name psql-job-matcher-restored --source-server psql-job-matcher --restore-time "<YYYY-MM-DDTHH:MM:SSZ>"`
3. Verify the restored server: connect, check the `vector` extension and row counts of key tables.
4. Point the application's DB host setting at the restored server, or copy data back with `pg_dump`/`pg_restore`.
5. Re-apply private endpoint and DNS configuration for the restored server.

## Geo-restore (region outage)
`az postgres flexible-server geo-restore --resource-group job-matcher --name psql-job-matcher-geo --source-server psql-job-matcher --location <paired-region>`

## Testing
Perform a PITR restore into a temporary server before go-live and at least every 6 months. Record the date, operator and result here, then delete the temporary server.

| Date | Operator | Result |
|------|----------|--------|
|      |          |        |
