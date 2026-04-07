# Malawi School Reporting System

A comprehensive web-based student management and report generation system designed for Malawi secondary schools. Features responsive data entry, PDF report generation, and professional Malawi flag-themed UI design.

## 🎯 Key Features

- **Multi-Form Support**: Data entry for Forms 1-4 with subject-specific mark recording
- **Responsive Design**: Mobile-friendly interface with sticky headers and no horizontal scrolling
- **PDF Report Generation**: Individual student report cards with professional formatting
- **Quick Actions**: One-click print buttons for each student, bulk operations support
- **Malawi Theming**: Beautiful UI with national flag colors (green, red, black, gold)
- **Real-time Validation**: Input validation and error handling for data integrity

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with custom ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **PDF Generation**: ReportLab library
- **Styling**: Custom CSS with Malawi flag color scheme

---

## Deployment on Render.com

This application is ready for deployment on Render.

### Using `render.yaml` (Recommended)
1. Push your code to a GitHub/GitLab repository.
2. On the Render dashboard, create a new **Blueprint** service.
3. Connect your repository. Render will automatically detect and use the `render.yaml` file to configure the web service.

### Manual Configuration
1. On the Render dashboard, create a new **Web Service**.
2. Set the **Build Command** to: `pip install -r requirements.txt`
3. Set the **Start Command** to: `gunicorn wsgi:app`

## Local development (optional) 💻
You can run the app locally using a small, opt-in helper included in `app.py` that mirrors the behavior of `run_web_app.bat` while keeping production-safe defaults.

Quick examples:
- Create a virtual environment and install requirements (one-time, opt-in):

  ```bash
  python app.py --setup
  ```

- Start the development server:

  ```bash
  python app.py --host 0.0.0.0 --port 5000 --debug
  ```

Command flags explained:
- `--setup`  : Create `.venv`, upgrade `pip`, and install `-r requirements.txt` into it. **Run locally only** (do NOT use on production hosts).
- `--host`   : Host to bind the server to (default: `0.0.0.0`).
- `--port`   : Port to listen on (default: `5000`).
- `--debug`  : Run Flask in debug mode (development only).

Notes & best practices:
- For production (Render, Heroku, etc.) use a WSGI server such as Gunicorn: `bash scripts/start_prod.sh` or `gunicorn wsgi:application -b 0.0.0.0:$PORT --workers 2`.
- **Populate sample data on startup (optional):** Set the environment variable `POPULATE_SAMPLE_DATA=1` (or `true`) to enable automatic sample data population. When enabled, `scripts/start_prod.sh` will run `setup_sample_data.py` to add sample students and `add_sample_marks.py` to populate marks before starting Gunicorn. These steps are non-fatal (the service will continue starting even if population scripts fail); use this for testing/demo environments only.
- To temporarily check template rendering on a deployed instance, set `ENABLE_TEMPLATE_DEBUG=1` and GET `/_debug/template-check` to surface template errors (do not leave this enabled in production).
