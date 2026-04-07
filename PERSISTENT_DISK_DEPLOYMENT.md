# Render Persistent Disk Deployment

If you prefer to keep using SQLite on Render, ensure you store the DB on a persistent disk so data isn't lost during redeploys.

Steps:
1. In Render service settings (Static / Web Service), add env var: `RENDER=true`.
2. Optionally set `RENDER_PERSISTENT_DIR` to your mounted path (e.g., `/opt/render/project/src/data`) if you use a different mount.
3. Confirm `DATABASE_PATH` is set to a path inside that persistent directory, e.g., `/opt/render/project/src/data/school_reports_persistent.db`.
4. Ensure backups are configured. This repo creates a backup script in the persistent `backups/` subdirectory automatically via `PersistentDataManager.setup_auto_backup()`.

Verification:
- Deploy the app, add a student or marks, then redeploy. The data should persist if `DATABASE_PATH` points to persistent storage.

Troubleshooting:
- If you see the log warning: "DATABASE_PATH does not appear to be on the configured persistent disk", check your `DATABASE_PATH` and `RENDER_PERSISTENT_DIR` values in Render.
- To test locally, set `RENDER=true` and `RENDER_PERSISTENT_DIR` to a local path and run the app; the code will create the directories automatically.
