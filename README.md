# Healthcare API

A Django REST Framework backend for user authentication, patient and doctor records, and patient–doctor assignments. The API uses JWT bearer tokens and PostgreSQL.

## Requirements

- Python 3.10 or newer
- PostgreSQL 14 or newer

## Run locally

1. Create and activate a virtual environment, then install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env`. Set a unique `SECRET_KEY`, your PostgreSQL `DB_USER` and `DB_PASSWORD`, and the correct `DB_PORT` (usually `5432` for a local PostgreSQL installation). Create a database named `healthcare` using pgAdmin or your preferred PostgreSQL tool.

3. Apply the database migrations, then start Django:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

The API is available at `http://127.0.0.1:8000/api/`. All routes return JSON.

## Browser dashboard

Open `http://127.0.0.1:8000/` to create an account or choose **Log in** if you already have one. After signing in, the dashboard links to patient records, the doctor directory, and doctor assignments. Each page includes forms to add records, update or remove records you own, and create or remove patient-doctor assignments. The REST endpoints remain available under `/api/` for API clients.

Use **Forgot password?** on the login page to request a reset link. In local development, Django prints reset emails in the server terminal. A deployed site needs an email service configured through its deployment environment for password reset delivery.

## Authentication

Register at `POST /api/auth/register/` with `name`, `email`, and `password`. Registration returns user data plus `access` and `refresh` JWTs. Log in at `POST /api/auth/login/` with `email` and `password`. Refresh an access token with `POST /api/auth/token/refresh/` and a JSON `refresh` value.

For protected endpoints, send `Authorization: Bearer <access-token>`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Create an account and receive tokens |
| POST | `/api/auth/login/` | Log in and receive tokens |
| POST | `/api/auth/token/refresh/` | Refresh an access token |
| GET, POST | `/api/patients/` | List your patients or create one |
| GET, PUT, PATCH, DELETE | `/api/patients/<id>/` | Read, update, or delete one of your patients |
| GET, POST | `/api/doctors/` | List all doctors or create one |
| GET, PUT, PATCH, DELETE | `/api/doctors/<id>/` | Read a doctor or update/delete a doctor you created |
| GET, POST | `/api/mappings/` | List your patient assignments or assign a doctor |
| GET, DELETE | `/api/mappings/<id>/` | List doctors for your patient ID, or delete your mapping ID |

Patient JSON fields: `name`, `age`, `gender`, `address`, and optional `phone`.

Doctor JSON fields: `name`, `specialization`, `email`, optional `phone`, and optional `address`.

Assignment JSON fields: `patient` and `doctor` (their integer IDs). Duplicate assignments are rejected. Patients and assignments are scoped to the signed-in user. Doctors can be listed by any signed-in user; only the doctor creator can change or delete that doctor.

## Notes

- Never commit `.env`; it is ignored by Git. Use a unique secret key and a strong, non-default database password. The app now refuses to start if `DB_USER` or `DB_PASSWORD` is missing or the sample password placeholder has not been replaced.
- `DEBUG=True` is for local development only. Before a public deployment, set `DEBUG=False`, configure the production `ALLOWED_HOSTS`, and serve the site over HTTPS. HTTPS redirects and secure session/CSRF cookies are enabled automatically when `DEBUG=False`. HSTS for all subdomains and browser preload should only be enabled after confirming every relevant subdomain uses HTTPS.
- Run `python manage.py createsuperuser` if you need Django admin access at `/admin/`.

## Test with Postman

Use `http://127.0.0.1:8000` as the base URL. First register or log in and copy the returned `access` token. For protected endpoints, select **Bearer Token** in Postman’s Authorization tab and paste the access token. Create a patient and doctor, then use their returned IDs in the mapping request. Exercise each endpoint and verify its status code and response.

The API returns the refresh token only from register/login responses; keep it private and do not include real tokens in screenshots, source files, or GitHub commits.
