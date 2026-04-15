# Project Overview

Flask-based catalog website for Russian tea shop "Чайнань". Static HTML/CSS/assets served from project root with JSON API for content management.

## Stack

- Python 3.11
- Flask + Werkzeug
- Gunicorn for production serving
- Static HTML pages (`index.html`, `admin.html`)
- Content stored in `content.json` (all site content) and `teas.json` (varieties, legacy sync)

## File Structure

- `index.html` — main public page (loads content dynamically from /api/content)
- `admin.html` — CMS admin panel (login required, section dropdown, image upload)
- `server.py` — Flask app with all API routes
- `content.json` — unified content store: modals (image+html), teas (desc+note+varieties), footer
- `teas.json` — tea varieties (auto-synced from content.json for backward compatibility)
- `chairman.png` — chairman photo served as static file

## API Routes

- `GET /api/content` — full content.json
- `POST /api/content` — save full content (auth required), also syncs teas.json
- `POST /api/upload` — upload image file, saves to root dir, returns URL (auth required)
- `GET /api/teas` — tea varieties from teas.json
- `POST /api/teas` — save varieties (auth required)
- `POST /api/login` — session login
- `POST /api/logout` — session logout
- `GET /api/me` — check login status

## Admin Panel (`/admin`)

- Login with password (env var `ADMIN_PASSWORD`, default `chainan2002`)
- Section dropdown: 6 modal sections + 7 tea catalog entries + footer
- **Modal sections**: image URL/upload + HTML textarea (empty = hardcoded template shown)
- **Tea sections**: description + note (multi-line) + varieties (one per line → shown as comma list)
- **Footer**: location + contact fields
- Save applies changes immediately to live site

## Modal System

- All nav section buttons open a single modal (`.tea-party-modal`)
- JS checks `siteContent.modals[key].html` first; falls back to hardcoded `<template>` elements
- If admin has saved HTML for a modal, it overrides the template
- `data-current-key` attribute used for CSS-targeting specific modals

## Deployment

- Gunicorn: `gunicorn --bind=0.0.0.0:5000 --reuse-port server:app`
- Flask sessions (signed cookies, `SECRET_KEY` env var)
- Content files (`content.json`, `teas.json`) must be writable in deployment
