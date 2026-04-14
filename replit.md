# Project Overview

This is a Flask web application for the Russian tea shop catalog “Чайнань”. It serves static HTML/CSS/assets from the project root and exposes JSON API endpoints for reading and updating tea varieties stored in `teas.json`.

## Stack

- Python 3.12
- Flask
- Gunicorn for production serving
- Static HTML pages (`index.html`, `admin.html`)
- JSON file storage (`teas.json`)

## Runtime

- Development command: `python3 server.py`
- Production command: `gunicorn --bind=0.0.0.0:5000 --reuse-port server:app`
- Web port: `5000`
- The Flask server binds to `0.0.0.0` for Replit preview compatibility.

## Key Files

- `server.py`: Flask app, static file serving, and tea/admin API routes
- `index.html`: Public tea catalog page
- `admin.html`: Password-protected tea assortment editor
- `teas.json`: Editable tea variety data
- `pyproject.toml`: Python dependency declaration
- `.replit`: Replit workflow and publishing configuration

## Configuration

- `SECRET_KEY`: Optional Flask session secret. Falls back to the current development default if unset.
- `ADMIN_PASSWORD`: Optional admin login password. Falls back to the current development default if unset.

## User Rules

- Do not change existing finished site structures, global styles, or unrelated page text unless the user explicitly asks for those exact areas to be changed.
- When editing a component or modal, limit changes to that component/modal and avoid touching global page styles.
