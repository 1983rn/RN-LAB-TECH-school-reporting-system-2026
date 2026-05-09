# Force Sync Push Script for Scholastic Record and Health Fixes
# This script ensures ALL changes are captured and pushed to GitHub
git add .
git commit -m "CRITICAL: Added /health route and fallback bulk print route to resolve 404s"
git push origin main
