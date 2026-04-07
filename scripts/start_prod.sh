#!/usr/bin/env bash
set -e

# Migrate database to persistent storage
python migrate_database.py

# Optional: run DB initialization/migrations here
python -c "import scripts.check_render_ready; print('Checked basic readiness')"

# Optional: populate sample data when POPULATE_SAMPLE_DATA env var is set (1/true/TRUE).
# These steps are non-fatal so the service will continue starting even if population fails.
if [ "${POPULATE_SAMPLE_DATA:-}" = "1" ] || [ "${POPULATE_SAMPLE_DATA:-}" = "true" ] || [ "${POPULATE_SAMPLE_DATA:-}" = "TRUE" ]; then
  echo "POPULATE_SAMPLE_DATA enabled: running sample data population (non-fatal on errors)"
  (python ../setup_sample_data.py || echo "Warning: sample student setup failed, continuing")
  (python ../add_sample_marks.py || echo "Warning: adding sample marks failed, continuing")
else
  echo "POPULATE_SAMPLE_DATA not set; skipping sample data population"
fi

# Start Gunicorn with 2 workers (adjust as needed)
exec gunicorn wsgi:application -b 0.0.0.0:${PORT:-10000} --workers 2
