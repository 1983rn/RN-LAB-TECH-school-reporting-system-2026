# Deploying to Render (Checklist)

This project includes a `render.yaml` and `wsgi.py` suitable for deploying to Render's Python service. Follow these steps when you are ready to deploy:

1. Environment variables (set on Render dashboard under Service > Environment > Environment Variables):
   - `SECRET_KEY` — set a secure random string (required for production).
   - `DATABASE_URL` — recommended: use Render's managed Postgres and set this to the DB URL.
   - `DEVELOPER_USERNAME` / `DEVELOPER_PASSWORD` — optional; used by the minimal developer login.

2. Use a managed Postgres for production (recommended) instead of SQLite — the filesystem is ephemeral on Render.
   - If using Postgres, update `school_database.py` connection logic to read `DATABASE_URL` (e.g., via `psycopg2` or `sqlalchemy`).

3. Build & start commands (already in `render.yaml`):
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn wsgi:application`

4. Static files:
   - `whitenoise` is included and `wsgi.py` wraps the app with WhiteNoise to serve `static/` content.

5. Start script (optional):
   - There is `scripts/start_prod.sh` which performs a basic readiness check (useful to run migrations in future) and then starts Gunicorn. If you prefer, update `render.yaml` to use this script as the `startCommand`.

6. Health check:
   - Endpoint: `/health` returns a simple JSON (`{'status': 'ok'}`); configure Render to use this path for service health checks.

5. Health check:
   - Endpoint: `/health` returns a simple JSON (`{'status': 'ok'}`), set Render service health check to use this path.

6. Database migrations & initial data:
   - Provide an initialization script or a migration mechanism; there are utility scripts in `scripts/`.

7. Logging & monitoring:
   - Render captures stdout/stderr; ensure your app logs to stdout for easy inspection.

8. Post-deployment:
   - Run `python scripts/check_render_ready.py` (or run it locally) to verify basic requirements.
   - Ensure `SECRET_KEY` and `DATABASE_URL` are set in Render dashboard.

If you'd like, I can:
- Add instructions to migrate the existing SQLite data to a Postgres instance.
- Add a `start.sh` that runs database migrations then starts gunicorn (and update `render.yaml` to use it).
