# TravelWorld Backend (Python / Flask)

A full-stack backend for the TravelWorld site — authentication, tours, bookings,
and an admin panel — built with **Flask** and **SQLite** (no separate database
install needed).

## 1. Prerequisites

- Python 3.9+

## 2. Setup

```bash
cd backend-python
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` already has sensible local defaults:
```
SECRET_KEY=change_this_to_a_long_random_secret
DATABASE_URL=sqlite:///travelworld.db
JWT_EXPIRES_IN_DAYS=7
PORT=5000
```

## 3. Add sample tours (optional but recommended)

```bash
python seed.py
```

Inserts 7 sample tours so the home page and tours page aren't empty.
`travelworld.db` (a SQLite file) is created automatically the first time you run the app.

## 4. Create your admin account

```bash
python create_admin.py admin@example.com yourpassword YourName
```

Only users with the `admin` role can log into `/admin` or add/edit/delete tours.

## 5. Set up the AI trip assistant (optional)

A chat bubble on every page lets visitors describe the trip they want, and
Gemini recommends real tours from your database. Google's free tier makes
this easy to try without adding a payment method.

1. Go to **aistudio.google.com/app/apikey** and sign in with a Google account.
2. Click **Create API key** — copy the value that appears.
3. Paste it into `.env` as `GEMINI_API_KEY=...`.

Without this key, the site still works fully — the chat widget will just reply
with a message saying the assistant isn't configured yet.

Note: the free tier has fairly low rate limits (a handful of requests per
minute) — fine for testing and demos, but if you outgrow it later you can add
a billing account in AI Studio for higher limits.

## 6. Run the server

```bash
python app.py
```

- API: `http://localhost:5000/api/v1`
- Admin panel: `http://localhost:5000/admin`

## 7. Run your frontend

Your `travelworld` frontend already points to `http://localhost:5000/api/v1`
in `js/script.js` — same URL, so nothing to change there. Open `index.html`
with a local server (VS Code's "Live Server" extension, or `npx serve`) rather
than double-clicking the file, to avoid browser CORS quirks with `file://` URLs.

## API Reference

| Method | Endpoint                                | Auth        | Description                  |
|--------|------------------------------------------|-------------|-------------------------------|
| POST   | /api/v1/auth/register                    | Public      | Create an account             |
| POST   | /api/v1/auth/login                       | Public      | Log in, returns JWT           |
| GET    | /api/v1/tours                            | Public      | All tours                     |
| GET    | /api/v1/tours/:id                        | Public      | One tour                      |
| GET    | /api/v1/tours/search/getFeaturedTours    | Public      | Featured tours (home page)    |
| GET    | /api/v1/tours/search/getTourCount        | Public      | Total tour count              |
| GET    | /api/v1/tours/search/getTourBySearch     | Public      | Filter by city/distance/size  |
| POST   | /api/v1/tours                            | Admin only  | Create a tour                 |
| PUT    | /api/v1/tours/:id                        | Admin only  | Update a tour                 |
| DELETE | /api/v1/tours/:id                        | Admin only  | Delete a tour                 |
| POST   | /api/v1/bookings                         | Logged-in   | Book a tour                   |
| GET    | /api/v1/bookings/my                      | Logged-in   | My bookings                   |
| GET    | /api/v1/bookings                         | Admin only  | All bookings                  |
| DELETE | /api/v1/bookings/:id                     | Admin only  | Delete a booking               |
| POST   | /api/v1/newsletter/subscribe             | Public      | Subscribe an email             |
| GET    | /api/v1/newsletter                       | Admin only  | List subscribers               |
| POST   | /api/v1/contact                          | Public      | Send a contact message         |
| GET    | /api/v1/contact                          | Admin only  | List contact messages          |
| POST   | /api/v1/assistant/chat                   | Public      | Chat with the AI trip assistant|

## Project structure

```
backend-python/
├── app.py               Flask app factory + entry point
├── config.py             Config loaded from .env
├── extensions.py         Shared SQLAlchemy instance
├── models.py             User, Tour, Booking (SQLAlchemy models)
├── auth_utils.py         JWT helpers + @token_required / @admin_required decorators
├── routes/
│   ├── auth.py            /api/v1/auth/*
│   ├── tours.py           /api/v1/tours/*
│   └── bookings.py        /api/v1/bookings/*
├── static/admin/          Admin panel (HTML/CSS/JS)
├── seed.py                Insert sample tours
├── create_admin.py        Create/promote an admin user
└── travelworld.db         SQLite database file (auto-created)
```

## How auth works

- Passwords are hashed with Werkzeug's `generate_password_hash` (never stored in plain text).
- Login returns a JWT signed with `SECRET_KEY`, valid for `JWT_EXPIRES_IN_DAYS`.
- Protected routes require an `Authorization: Bearer <token>` header.
- `@admin_required` checks the logged-in user's `role` field.

## Notes for later (deploying)

SQLite is great for local development but for hosting, you'll likely swap
`DATABASE_URL` to a hosted Postgres database (e.g. on Render or Railway) —
everything else in the code stays the same since SQLAlchemy abstracts the
database engine.
