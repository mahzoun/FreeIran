# Memorial Archive

A respectful memorial and documentation archive built with Django, Django REST Framework, and PostgreSQL.

## Features
- Public listing and profile pages with verification status
- Multiple photos per profile with gallery slider
- Sources with credibility scoring
- Tagging and filtering
- Submissions workflow with rate limiting
- Admin dashboard with audit logs
- REST API with pagination, filtering, search
- Dark/Light mode toggle and accessible UI

## Tech Stack
- Django + Django REST Framework
- PostgreSQL
- Django Templates + Bootstrap
- Docker + docker-compose

## Setup (Local)
1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and update values.
3. Run migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_groups
```

4. (Optional) Seed data:

```bash
python manage.py seed_data
```

5. Run the server:

```bash
python manage.py runserver
```

Visit `http://localhost:8000`.

## Docker

```bash
docker-compose up --build
```

The app will be available at `http://localhost:8000`.

## API
Base path: `/api/v1/`
- `/api/v1/victims/`
- `/api/v1/photos/`
- `/api/v1/sources/`
- `/api/v1/tags/`
- `/api/v1/suggest/?q=...`

## Roles
- Admin: full control (superuser)
- Moderator: add/edit/view (run `python manage.py setup_groups` and assign users to the `Moderator` group)
- Public: read-only access to web and API

## Backup
Use `scripts/backup.sh` to export a PostgreSQL dump. Configure credentials via `.env`.

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```

## Notes
- `family_contact_private` is stored but never exposed publicly.
- Unverified profiles are clearly labeled.
- Sources should be provided whenever possible.
