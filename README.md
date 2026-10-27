# CareDesk — Healthcare Management API

A Django REST Framework and PostgreSQL application for registering users, managing patient and doctor records, and assigning doctors to patients. It includes JWT authentication and a small browser dashboard for trying the main workflows.

## Contents

- [Features](#features)
- [Run locally](#run-locally)
- [Try the dashboard](#try-the-dashboard)
- [API guide](#api-guide)
- [Access rules](#access-rules)
- [Try it with Postman](#try-it-with-postman)

## Features

- Register and log in with email and password; receive JWT access and refresh tokens.
- Create, view, update, and delete patient and doctor records through REST endpoints.
- Assign doctors to patients and remove assignments.
- Validate request data and prevent duplicate patient–doctor assignments.
- Restrict patient and assignment data to the signed-in user; protect changes to doctor records by their creator.
- Use a browser dashboard for account registration, login, and record management.

## Run locally

**Requirements:** Python 3.10 or newer and PostgreSQL 14 or newer.

1. Create a PostgreSQL database named `healthcare` in pgAdmin or your preferred PostgreSQL tool.
2. In the project folder, create and activate a virtual environment, then install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`. Set a unique `SECRET_KEY` and your local PostgreSQL username and password. The example uses port `5432`; change `DB_PORT` if your PostgreSQL server uses another port.

   ```powershell
   Copy-Item .env.example .env
   ```

4. Apply migrations and start the development server:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

The local app runs at `http://127.0.0.1:8000/`; the API root is `http://127.0.0.1:8000/api/`.

## Try the dashboard

Open [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/) and register or log in. Use the navigation to manage patients, doctors, and assignments. The login page also has a password-reset link; in local development, Django prints the reset email and link in the server terminal.

## API guide

All API routes start with `http://127.0.0.1:8000/api/`. Register or log in first, then send the access token on protected requests:

```http
Authorization: Bearer <access-token>
```

### Authentication

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register with `name`, `email`, and `password`; returns user data and JWT tokens |
| POST | `/api/auth/login/` | Log in with `email` and `password`; returns user data and JWT tokens |
| POST | `/api/auth/token/refresh/` | Get a new access token using a `refresh` token |

Example registration body:

```json
{
  "name": "Asha Sharma",
  "email": "asha@example.com",
  "password": "Choose-a-strong-password"
}
```

### Patients

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET, POST | `/api/patients/` | List your patients or create a patient |
| GET, PUT, PATCH, DELETE | `/api/patients/<id>/` | Retrieve, update, or delete one of your patients |

Patient fields: `name`, `age`, `gender`, `address`, and optional `phone`. The API sets the creator from the authenticated account.

### Doctors

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET, POST | `/api/doctors/` | List doctors or create a doctor |
| GET, PUT, PATCH, DELETE | `/api/doctors/<id>/` | Retrieve, update, or delete a doctor |

Doctor fields: `name`, `specialization`, `email`, optional `phone`, and optional `address`. Any authenticated user can list doctors; only the doctor’s creator can update or delete that record.

### Patient–doctor assignments

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET, POST | `/api/mappings/` | List your assignments or assign a doctor to your patient |
| GET | `/api/mappings/<patient_id>/` | List doctors assigned to that patient |
| DELETE | `/api/mappings/<mapping_id>/` | Remove an assignment by its mapping ID |

Assignment request body:

```json
{
  "patient": 1,
  "doctor": 1
}
```

Use the patient and doctor IDs returned by their API endpoints. A patient can’t be assigned to a doctor twice.

## Access rules

- Patient endpoints require authentication and return only patients created by the signed-in user.
- Users can assign doctors only to their own patients; their assignment lists are scoped to their patients.
- Authenticated users can browse the doctor directory. Only a doctor’s creator can edit or delete it.
- Passwords are write-only in API responses. Keep access and refresh tokens private.

## Try it with Postman

1. Register or log in using the endpoints above; copy the returned `access` token.
2. For protected requests, choose **Authorization → Bearer Token** and paste that token.
3. Create a patient and a doctor, then use their returned integer IDs in a `POST /api/mappings/` request.
4. Try the list, detail, update, and delete routes in the tables above.

## Configuration and safety

- Keep `.env` local. It is excluded from Git; commit `.env.example` instead. Replace all sample secret and database-password values before running the app.
- `DEBUG=True` is for local development. Before deployment, set `DEBUG=False`, configure production `ALLOWED_HOSTS`, and serve over HTTPS.
- Optional Django admin access: create an admin account with `python manage.py createsuperuser`, then open `/admin/`.
