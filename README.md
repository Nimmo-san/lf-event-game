# Lightning Flight

An event/booth game built for Lightning Fibre. Players run through an
obstacle course collecting "glowbolts," submit a score, and can opt in to
a leaderboard with their name, company, and email. Built to work
booth-side on flaky wifi: gameplay is played and stored offline-first,
then synced to the backend once a connection is available.

An admin dashboard (password-protected) shows live analytics — score
distributions, play volume over time, top companies — and lets staff
export leaderboard/marketing contacts as CSV.

## Tech stack

- **Frontend** — Vue 3 (TypeScript) + Vite, packaged as an installable
  PWA (`vite-plugin-pwa`) with an IndexedDB-backed local store (`idb`)
  for offline play and deferred sync. Charts on the admin dashboard use
  `chart.js`.
- **Backend** — FastAPI + SQLAlchemy on SQLite, with rate limiting
  (`slowapi`) on public-facing endpoints.

## Project structure

```
src/                  Frontend (Vue 3 + TS)
  components/         Game UI, leaderboard, dashboard widgets
  game/                Canvas game engine (grid, patterns, collisions, rendering)
  storage/             IndexedDB models + offline sync queue
  services/            API clients, network status, sync manager
  views/               Routed pages (game, leaderboard, admin dashboard/export)
  router/              Vue Router config

backend/
  app/
    main.py            FastAPI app, CORS, router registration
    database.py         SQLAlchemy engine/session setup
    models/             ORM models (game results, leaderboard, admin sessions)
    routes/             API routes (players, leaderboard, admin)
    schemas/            Pydantic request/response schemas
    rate_limit.py        slowapi limiter config
    scoring.py           mirrors Game.ts's scoring formula server-side
    config_validation.py fail-fast checks for required prod env vars
  alembic/             DB migrations (see alembic/README for status)
  tests/
  requirements.txt
```

## Getting started

### Frontend

```bash
npm install
npm run dev       # starts Vite dev server (http://localhost:5173)
npm run build     # type-checks (vue-tsc) and builds for production
npm run preview   # serves the production build locally
npm test          # runs the Vitest unit tests (src/**/*.test.ts)
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API serves on `http://localhost:8000` by default, with an
auto-generated OpenAPI doc at `/docs`. A local SQLite database is
created automatically under `backend/data/` on first run.

### Environment variables (backend)

| Variable          | Purpose                                                                 |
| ------------------ | ------------------------------------------------------------------------ |
| `FRONTEND_URL`     | Production frontend origin, added to the CORS allow-list.               |
| `DATABASE_DIR`     | Absolute path for the SQLite file (points at Render's persistent disk in production; defaults to `backend/data` locally). |
| `ADMIN_EXPORT_KEY` | Shared secret required to log in to the admin dashboard.                |
| `ENVIRONMENT`      | Set to `production` to mark the admin session cookie `secure`.          |

## API overview

All game/leaderboard routes are prefixed `/api`; admin routes are
prefixed `/api/admin` and require an authenticated session cookie
(see `ADMIN_EXPORT_KEY` above).

- `POST /api/games` — submit a completed game's score/duration.
- `POST /api/leaderboard/entries` — opt a submitted game into the leaderboard.
- `GET /api/leaderboard` — top 10 leaderboard entries.
- `GET /api/leaderboard/rank/{player_id}` — a specific player's rank.
- `POST /api/admin/login` / `POST /api/admin/logout` / `GET /api/admin/session`
- `GET /api/admin/entries` — searchable/filterable leaderboard contacts.
- `POST /api/admin/export/marketing` — CSV export of contacts.
- `GET /api/admin/analytics` — aggregate play/leaderboard stats for the dashboard.
- `GET /health` — health check.

## Deployment

This project is deployed on **Render**: the frontend and backend are
deployed as separate Render services, with the backend's SQLite database
living on a Render persistent disk (its path is provided via
`DATABASE_DIR`, not committed to the repo). Environment variables above
are configured in the Render dashboard per service.

The backend runs as plain `uvicorn app.main:app` (no `--proxy-headers`
flag), so `app/rate_limit.py` reads the real client IP straight from
`X-Forwarded-For` itself rather than relying on uvicorn's own
proxy-trust logic — this assumes Render's edge/load balancer is the
only path to the service (true for a standard Render web service,
which isn't otherwise directly reachable from the public internet).

### Database migrations

Schema changes now ship as Alembic migrations (`backend/alembic/`)
instead of hand-editing the production database. This is mid-rollout:
`app.main` still runs `Base.metadata.create_all()` on startup, and a
one-time production cutover step (`alembic stamp head` on the Render
DB, then updating Render's start command to run `alembic upgrade
head` before `uvicorn`) hasn't happened yet. See
`backend/alembic/README` for the exact steps and current status
before making a model change that needs a real migration.

## Contributing

All changes — including from maintainers — go through a pull request.
Do not push directly to `main`. Open a PR from a feature branch, and
merge only once it's reviewed.
