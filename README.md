# AnimeTracker API

A RESTful API inspired by MyAnimeList, built with **FastAPI + PostgreSQL + JWT auth**.  
Deployable on AWS Free Tier (EC2 + RDS).

## Features

- User registration and JWT authentication
- Search anime via [Jikan](https://jikan.moe/) (unofficial MAL API) with local caching
- Manage your personal anime list (status, rating, progress, notes)
- Filter list by watch status
- Auto-generated interactive docs at `/docs`

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111 |
| Database | PostgreSQL (prod) / SQLite (dev) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | JWT via python-jose + passlib/bcrypt |
| External API | Jikan v4 (MyAnimeList) |
| Containerisation | Docker + docker-compose |
| Deployment | AWS EC2 + RDS (Free Tier) |

## Quick Start (local)

```bash
# 1. Clone and set up environment
git clone https://github.com/xNoll/animetracker.git
cd animetracker
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — at minimum, set a strong SECRET_KEY

# 3. Run (SQLite by default, zero config)
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs
```

## Quick Start (Docker + PostgreSQL)

```bash
docker-compose up --build
# Visit http://localhost:8000/docs
```

## API Endpoints

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Get JWT token |

### Anime
| Method | Path | Description |
|---|---|---|
| GET | `/anime/search?q=...` | Search via Jikan |
| GET | `/anime/browse` | Browse cached anime |
| GET | `/anime/{mal_id}` | Get single anime |

### My List (requires JWT)
| Method | Path | Description |
|---|---|---|
| GET | `/list/` | Get my list (optional `?status=watching`) |
| POST | `/list/` | Add anime to list |
| PUT | `/list/{mal_id}` | Update entry |
| DELETE | `/list/{mal_id}` | Remove from list |

### Watch Status Values
`plan_to_watch` · `watching` · `completed` · `on_hold` · `dropped`

## Running Tests

```bash
pytest tests/ -v
```

## Deployment (AWS Free Tier)

See [DEPLOY.md](DEPLOY.md) for step-by-step guide to deploying on EC2 + RDS.

**Free Tier resources used:**
- EC2 `t2.micro` — runs the FastAPI app in Docker
- RDS `db.t3.micro` (PostgreSQL) — managed database
- Both free for 12 months (750 hours/month each)

## Project Structure

```
animetracker/
├── app/
│   ├── main.py          # FastAPI app + router registration
│   ├── config.py        # Settings from environment variables
│   ├── database.py      # SQLAlchemy engine + session + Base
│   ├── models/          # ORM models (DB schema)
│   ├── schemas/         # Pydantic models (input/output validation)
│   ├── routers/         # Endpoint definitions
│   ├── crud/            # Database operations (separated from routes)
│   └── core/
│       └── security.py  # Password hashing + JWT
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```
