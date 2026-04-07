# Postgres Deployment on Render

Follow these steps to use a managed Postgres DB for the app (recommended):

1. Provision a Postgres instance on Render or another provider.
2. In Render service settings, set the following environment variables:
   - `DATABASE_URL` set to the Postgres connection string (e.g., `postgres://user:pass@host:port/dbname`).
   - `RENDER=true` (optional; used by the persistent manager)
3. Add `SQLAlchemy` and `psycopg2-binary` to `requirements.txt` (already added by this change).
4. Deploy. The app will detect `DATABASE_URL` and initialize a Postgres schema automatically.
5. Optionally migrate existing SQLite data using `migrate_sqlite_to_postgres.py`:
   - Set `DATABASE_URL` to the target Postgres and `DATABASE_PATH` to your SQLite DB path.
   - Run `python migrate_sqlite_to_postgres.py` to copy tables.

Notes:
- This repository keeps compatibility with SQLite for local development. If `DATABASE_URL` is not set, the app uses a local SQLite database file.
- Backups: rely on your managed DB's backup features; for SQLite, `PersistentDataManager` creates backups.
