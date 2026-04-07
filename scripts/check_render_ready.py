"""Simple readiness checks for Render deployment
Runs a few quick local checks to surface common deployment issues.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(ROOT, '..'))

print('Checking Render readiness...')

# Check requirements.txt for important packages
reqs = open(os.path.join(REPO_ROOT, 'requirements.txt')).read()
missing = []
for pkg in ['gunicorn', 'whitenoise', 'Flask']:
    if pkg not in reqs:
        missing.append(pkg)

if missing:
    print('WARNING: requirements.txt is missing:', ', '.join(missing))
else:
    print('OK: requirements contain gunicorn, whitenoise, and Flask')

# Check render.yaml presence and contents
render_yaml = os.path.join(REPO_ROOT, 'render.yaml')
if not os.path.exists(render_yaml):
    print('ERROR: render.yaml not found')
    sys.exit(1)
else:
    print('OK: render.yaml exists')
    content = open(render_yaml).read()
    if 'gunicorn' not in content:
        print('WARNING: render.yaml startCommand does not reference gunicorn')
    else:
        print('OK: render.yaml uses gunicorn as start command')

# Check for SECRET_KEY env
if os.environ.get('SECRET_KEY'):
    print('OK: SECRET_KEY is set in environment')
else:
    print('WARNING: SECRET_KEY is not set; set SECRET_KEY in Render env vars before deploying')

print('\nChecklist:')
print('- Ensure SECRET_KEY is set in Render dashboard env vars')
print('- Prefer a managed Postgres (DATABASE_URL) instead of SQLite for production')
print('- Add database migrations / init step to start command if needed')
print('\nExiting with status 0 (informational)')
