# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development server
```bash
# Activate the virtual environment first
pipenv shell

# Run the development server
./manage.py runserver --settings=talesofvalor.settings.local

# Apply migrations
./manage.py migrate --settings=talesofvalor.settings.local

# Create new migrations after model changes
./manage.py makemigrations --settings=talesofvalor.settings.local

# Create a superuser
./manage.py createsuperuser --settings=talesofvalor.settings.local
```

### CSS/Frontend
```bash
# Compile SASS to CSS (watches for changes, runs continuously)
gulp

# Install node packages (first time setup)
npm install
```

### Running tests
Tests are Selenium-based browser tests — they require the dev server to be running first:
```bash
cd talesofvalor/tests
python SimpleTests.py
```

### Deployment
```bash
fab deploy --environment stage --migrate
fab deploy --environment production --migrate --branch main
```

## Settings

Settings are split by environment in `talesofvalor/settings/`:
- `common.py` — shared base settings
- `local.py` — local development (not committed; copy from `stage.py`)
- `stage.py` / `production.py` — server environments

Always pass `--settings=talesofvalor.settings.local` to management commands locally. The `DJANGO_SETTINGS_MODULE` env var can also be set via direnv (see `envrc_template`).

Local email: set `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` in `local.py` to print emails to the console instead of sending them.

Database: production/staging use MySQL (`talesof_rhiven`); local development defaults to SQLite (`project.db`) in `common.py` but can be overridden in `local.py` to use MySQL.

## Architecture

This is a **Django 3.x** LARP (live action role-playing game) management application for "Tales of Valor." It uses **django-cms** for CMS pages alongside the custom apps.

### Django apps (`talesofvalor/`)

Each app follows the standard Django structure (`models.py`, `views.py`, `urls.py`, `forms.py`, `admin.py`, `templates/`).

- **players** — `Player` model (one-to-one with Django `User`), `Registration`, `RegistrationRequest`, and `PEL` (Post-Event Letter). A `Player` is created automatically via `post_save` signal when a `User` is created.
- **characters** — `Character` model (many-to-one with `Player`; only one can be `active_flag=True` at a time for non-staff). Characters have CP (character points), origins, headers, and skills. The `skillhash` and `skill_cost` properties compute available skills and dynamic costs based on Rules.
- **skills** — `Skill`, `Header`, `HeaderSkill` models. Skills live under Headers; `HeaderSkill` is the through table holding the cost of a skill in a specific header.
- **origins** — `Origin` model (type: `TRADITION` or `PEOPLE`). Characters have two origins that can modify skill costs and grant free skills via Rules.
- **rules** — `Rule`, `Prerequisite`, `PrerequisiteGroup` models. Rules use Django's `ContentType` framework to attach cost modifications and free grants to Skills, Headers, or Origins generically.
- **events** — `Event` and `EventRegistrationItem` models. Registration items bundle one or more events for purchase (with a price).
- **registration** — Handles the registration flow. Not to be confused with `players.Registration` (the completed record) vs `players.RegistrationRequest` (the pending PayPal order).
- **betweengameabilities** — Skills/abilities used between events.
- **attendance** — Tracks player attendance at events.
- **charactermessages** — Messages from staff to characters.
- **comments** — Comment system.
- **reports** — Staff reporting views.
- **services** — Utility endpoints (PayPal webhooks, AJAX helpers).

### Key cross-cutting patterns

**CP system**: Characters have `cp_initial`, `cp_spent`, and `cp_available`. Spending CP updates both the character and triggers recalculations. `STARTING_POINTS = 30`, `POINT_CAP = 25`.

**Rules engine**: `Rule` objects use `GenericForeignKey` to attach to Skills, Headers, or Origins. Rules can reduce skill costs (`new_cost`) or grant skills/headers for free (`free=True`). `Character.skill_cost()` resolves the effective cost by finding the minimum from all applicable rules.

**Prerequisites**: `Prerequisite` and `PrerequisiteGroup` are also generic-FK based, checked via `Character.check_prerequisites()`, `check_header_prerequisites()`, and `check_skill_prerequisites()`.

**PayPal integration**: `PayPalClientMixin` in `talesofvalor/mixins.py` wires PayPal SDK. The flow is: player creates a `RegistrationRequest` → PayPal payment → `RegistrationRequest.request_complete()` converts it to one or more `Registration` records and emails staff.

**User impersonation**: `django-hijack` is installed; staff/admin can impersonate players. Middleware and permission check are configured in `common.py`.

**Wiki**: `django-wiki` is installed at `/wiki/` with notifications via `django-nyt`.

**CMS**: `django-cms` serves the public-facing pages. Custom app pages plug into CMS via apphooks defined in each app.

### Frontend

SASS source lives under `static_global/`. Gulp compiles it to CSS. The gulpfile uses `gulp-sass` (Dart Sass). Template files are in `talesofvalor/templates/` (global) and `<app>/templates/` (per-app).

### Groups and permissions

The app uses Django groups for access control. Key group names referenced in code: `"Staff"`, `"Admin"`. Custom permissions include `change_any_player`, `view_any_player`, `register_as_cast`, `reset_points`.
