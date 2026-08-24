# Production safety & testing review — August 2026

## Context

Before this review, `lightning-flight` had no CI, no automated tests
(backend or frontend), and several places where the code silently
trusted things it shouldn't have — client-submitted scores, an
unset/misspelled environment variable, a proxy configuration that
didn't match what the rate limiter assumed. None of this was
necessarily wrong on the happy path; it just meant failures would
show up as a confused user or a quiet data-integrity problem instead
of a clear error.

This doc records what was found, what shipped to fix it, how to tell
the codebase is actually stronger as a result (not just "more code"),
and — the part meant to outlast this specific review — how to keep
catching this class of issue going forward instead of rediscovering
it from scratch next time.

Everything below shipped as a separate, reviewed PR, in the order
listed, per the repo's "every change goes through a PR" rule (itself
the first thing this review added).

## What shipped

| # | PR | Issue found | Fix |
|---|----|-------------|-----|
| 0 | #1 | No `CONTRIBUTING`-style rule; README didn't document the project | Wrote the README; added the "always requires a PR" rule everything after this rode on |
| 1 | #2 | No CI at all — nothing ran on push or PR | GitHub Actions: typecheck+build (frontend), pytest (backend) |
| 2 | #3 | Zero backend tests | pytest scaffolding + first tests for the game/leaderboard routes |
| 3 | #4 | Leaderboard score had no relationship to reported duration/lightning — a direct API call could claim any score | Server-side `max_plausible_score()` mirroring the client's scoring formula; rejects anything above it |
| 4 | #5 | `/health` returned 200 unconditionally, even with a dead database | Runs `SELECT 1`; returns 503 on failure |
| 5 | #6 | A typo'd/missing `ENVIRONMENT` silently disabled the admin cookie's `Secure` flag — browsers then drop the cookie with no error anywhere | Fail-fast startup validation of `ENVIRONMENT`, `ADMIN_EXPORT_KEY`, `FRONTEND_URL` |
| 6 | #7 | No logging anywhere — a rejected submission or failed admin login left no trace | `logging` wired into every rejection path + admin auth events; found admin routes had **zero** test coverage while doing this |
| 7 | #8 | Schema changes required hand-editing the production DB (already happened once — see the commented-out columns) | Alembic scaffold + a baseline migration proven to match current models exactly |
| 8 | #9 | Zero frontend tests | Vitest unit tests for the three pure game-logic modules |
| 9 | #10 | SQLite's default journal mode blocks readers during a write; rate limiting keyed off Render's proxy IP, not the real visitor | WAL mode + explicit lock timeout; rate limiter now reads `X-Forwarded-For` |

Test count: **0 → 65** automated tests (43 backend, 22 frontend), all
running in CI on every PR.

## The fixes, in detail

### 1. CI (#2)

`.github/workflows/ci.yml` runs on every PR/push to `main`: a
`frontend` job (`npm run build`, which runs `vue-tsc -b` first, so
it's a real typecheck; later extended to also run `npm test`), and a
`backend` job (`pytest`, initially just an import smoke test before
#3 added real tests). This is the foundation everything else needed —
without it, nothing else on this list would have had automated
proof it kept working.

**Still needs a human:** GitHub branch protection requiring these
checks to pass isn't something a PR can turn on — that's a repo
settings change for whoever administers this repo.

### 2. Backend test scaffolding (#3)

`tests/conftest.py` points `DATABASE_DIR` at a throwaway temp
directory *before* `app.database` is ever imported, so the suite
never touches the real dev database, and resets both the DB tables
and the rate limiter before every test (the FastAPI `app` and its
`Limiter` are process-wide singletons shared across the whole test
session — without the reset, later tests would see earlier tests'
rows, or trip a rate limit purely from test volume).

**Found while writing this:** `routes/players.py`'s own
`if payload.duration <= 0` check is unreachable — the Pydantic schema
already has `Field(gt=0)`, so that case 422s before the handler body
ever runs. Documented as a test rather than "fixed," since fixing it
wasn't this PR's job.

### 3. Score plausibility check (#4)

The single highest-value fix. `Game.ts` computes score entirely
client-side; the backend only checked flat caps
(`score <= 100_000`, `duration <= 300s`) with **no relationship**
between score, duration, and lightning collected — a direct
`POST /api/games` call could claim top score for zero actual
gameplay.

`backend/app/scoring.py` mirrors `Game.ts`'s scoring constants
(`SURVIVAL_RATE`, `LIGHTNING_BASE_SCORE`, `COMBO_STEP`,
`COMBO_MAX_MULTIPLIER`, `ROUND_DURATION`) and computes the *exact*
ceiling a given duration + lightning count can produce — not a fuzzy
heuristic, since the combo multiplier is monotonic and never resets
mid-run (a collision always ends the round). Verified by hand-
computing a known case (45.5s + 12 bolts = exactly 1996 points)
before trusting the code. Also tightened the duration cap from a
stale flat 300s to `ROUND_DURATION` (120s) + a small jitter buffer,
matching what the client can actually produce.

### 4. `/health` checks the database (#5)

Was `return {"status": "ok"}`, unconditionally. Now runs a trivial
query through the real `get_db` dependency and returns 503 if it
raises — so a Render disk problem shows up as a red health check
instead of a green one hiding real 500s underneath it.

### 5. Fail-fast environment validation (#6)

`backend/app/config_validation.py`. The root issue:
`routes/admin.py`'s `IS_PRODUCTION = os.environ.get("ENVIRONMENT") == "production"`
silently degrades to `False` for *any* value that isn't the exact
string `"production"` — including a typo. That flips the admin
session cookie from `Secure` to not-`Secure` while it's still
`SameSite=None`, and browsers discard such a cookie outright, with
zero server-side error. Two sibling issues, same shape:
`ADMIN_EXPORT_KEY` unset makes every admin login 401 with nothing
explaining why; `FRONTEND_URL` unset silently breaks CORS for the
production frontend.

Now the app crashes at startup with a specific error if
`ENVIRONMENT` isn't `production`/`development`/unset, or if a
production deploy is missing `ADMIN_EXPORT_KEY`/`FRONTEND_URL`.
Verified end-to-end (not just via the unit tests) by actually
importing `app.main` under four real environments and watching each
one crash-with-explanation or succeed as expected.

### 6. Backend logging (#7)

`logging.basicConfig()` once in `main.py` (plain stdout — Render
already captures that as the service's log stream). Warnings on
every rejected `/api/games` and `/api/leaderboard/entries` submission
and every failed admin login; info-level logs on successful admin
login/logout as a small audit trail.

**Found while writing this:** the admin router had **zero** test
coverage, and the reason was structural — `ADMIN_EXPORT_KEY` is read
once at import time, and the test suite never set it, so admin login
was *guaranteed* to 401 regardless of what was tested. Fixed
`conftest.py` to set a known test key before import, and added
`tests/test_admin.py`.

### 7. Alembic migrations (#8)

The biggest infrastructure change, and the one with the most care
taken around blast radius. `models/game.py` and
`models/leaderboard.py` already carry commented-out columns (`email`,
`marketing_consent`) — proof a schema change already had to happen by
hand once, editing the production database directly.

Added a full Alembic scaffold and a baseline migration, verified two
ways: applying it to a fresh DB produces the exact schema
`Base.metadata.create_all()` produces, and `alembic check` afterward
reports zero drift.

**Deliberately did not remove `Base.metadata.create_all()`** from
`main.py`. The existing Render database already has all three tables
— built by `create_all()`, not Alembic — so Alembic doesn't know
that yet. Removing `create_all()` now would mean the next deploy
boots against an empty schema and crashes on the first query. The
one-time cutover (`alembic stamp head` on the Render DB, then a
Render start-command change to run `alembic upgrade head` before
`uvicorn`) needs Render console access this review didn't have —
it's documented step by step in `backend/alembic/README`, waiting on
whoever owns the Render dashboard.

**Found while building this:** two real bugs, only visible once the
*whole* test suite ran together, not just the new migration test in
isolation — `env.py` was unconditionally overwriting any
already-set `sqlalchemy.url` (broke pointing Alembic at a scratch
test DB), and `fileConfig()`'s default `disable_existing_loggers=True`
silently killed every `app.routes.*` logger (from #7) for the rest of
the test process the moment the migration test ran. Both fixed with
comments explaining why, since neither failure mode is obvious from
reading Alembic's own generated boilerplate.

### 8. Frontend unit tests (#9)

Vitest, targeting the three modules with zero DOM dependency:
`PatternValidator`, `ReachabilityValidator`, `CollisionSystem`. For
the collision geometry tests specifically, expected hitbox
coordinates were hand-computed *before* writing the assertions, so
the test run was a genuine check of the coordinate math, not just
"code and test happen to agree."

**Found while writing this:** `validateRow`'s "lightning overlaps
obstacle" branch is unreachable — `CellType` models each cell as a
single value, so there's no way to construct a test input that trips
it through the type-safe API. The code's own comment already frames
this as a guard against "future procedural generation," so it's
intentional, just untestable today.

### 9. SQLite WAL mode + real-IP rate limiting (#10)

Two independent fixes bundled since both were "the deployed
configuration doesn't match what the code assumes."

**WAL mode**: SQLite's default journal mode blocks every reader for
the duration of a writer's transaction — a live event's
`GET /api/leaderboard` traffic landing next to a `POST /api/games`
burst is exactly the shape of thing that becomes "database is
locked." `database.py` now enables WAL via `PRAGMA` on every new
connection, and makes the (already-defaulted) 5-second lock-wait
timeout explicit instead of implicit.

**Rate limiting**: before writing any code, asked the repo owner how
the backend is actually started on Render — confirmed plain
`uvicorn app.main:app`, no `--proxy-headers` flag. That meant
`request.client.host` was Render's own proxy IP for *every* request,
so every visitor — including anyone brute-forcing the admin login —
shared one rate-limit bucket. `rate_limit.py` now reads the real
client IP from `X-Forwarded-For` directly, which is safe to trust
since Render's edge is the only path to the service.

Verified the fix mattered, not just that a test was green: reverted
`rate_limit.py` to the old `key_func`, re-ran the new test, watched
it fail exactly as predicted (both simulated visitors sharing one
bucket), then restored the fix and watched it pass.

## How the codebase is stronger now

- **Nothing merges untested.** Every PR runs a typecheck, a frontend
  build, and both test suites — previously nothing ran at all.
- **The leaderboard can't be trivially forged.** A submitted score
  has to be achievable for the reported duration and lightning
  count, computed the same way the game itself computes it.
- **A broken deploy fails loudly, not quietly.** Misconfigured
  production env vars now crash the app at startup with a specific
  error, instead of coming up looking healthy and breaking admin
  auth or CORS silently.
- **Incidents are debuggable.** Rejected requests, failed admin
  logins, and successful admin sessions are all logged now; the
  health check reflects the database's real state instead of a
  hardcoded "ok."
- **Schema changes have a real mechanism.** Alembic exists and its
  baseline is proven correct; the next model change doesn't have to
  mean hand-editing the production database again.
- **The backend holds up better under concurrent load** (WAL mode),
  and **rate limiting/abuse protection actually differentiates
  visitors** instead of collapsing behind Render's proxy IP.

## How to avoid repeating these

Patterns that produced more than one finding above, worth carrying
forward as habits:

1. **Write down deployment assumptions instead of leaving them
   implicit.** The cookie `Secure` flag, the rate limiter's trusted
   IP source, and the Alembic cutover were all cases where the code
   silently assumed something about the environment it runs in. When
   behavior depends on how something is deployed, say so in a
   comment (or better, validate it — see `config_validation.py`) —
   don't let it stay implicit until it breaks.
2. **Client-submitted data feeding a scoreboard/reward needs
   server-side derivation, not just bounds-checking.** "Is the score
   under 100,000" is a different (much weaker) guarantee than "is
   this score achievable." Any time a client computes something that
   later gets trusted (a score, a price, a discount), ask whether the
   server can independently derive or verify it.
3. **A commented-out model field is a signal, not a stopping
   point.** It means a migration tool is needed *before* the next
   change, not after. Two columns were already commented out before
   Alembic existed here.
4. **New required-in-production env vars need startup validation,
   not just `os.environ.get()`.** An unset or malformed value should
   fail the deploy, not degrade some unrelated behavior silently.
5. **Before trusting a regression test, break the thing it's
   supposed to catch and confirm it actually fails.** This caught
   real gaps twice this review (the rate-limiter test, indirectly the
   Alembic drift test) — a test that's never seen its bug is an
   unverified assumption wearing a green checkmark.
6. **Run the whole suite together before merging a new piece of
   infrastructure, not just its own new tests in isolation.** Both
   bugs found while building Alembic (#8) only showed up when the
   full test suite ran as one process — an isolated `pytest
   tests/test_migrations.py` would have looked fine on its own.

## Where to keep looking for improvements

A repeatable process, not a one-time checklist — useful for the next
review of this repo or any other:

- **Trace every trust boundary.** Client → server (form fields, API
  payloads), env var → runtime behavior, third-party proxy → app,
  user input → SQL/shell/file path. At each one, ask: what happens if
  this is missing, malformed, or actively adversarial? Most of this
  review's findings live exactly on one of these boundaries.
- **Grep for `TODO`, `FIXME`, and commented-out code.** They mark
  known-incomplete decisions someone already flagged and moved on
  from. `players.py` still has two `# needs to change TODO` comments
  on the flat score/lightning caps — worth another look once there's
  real usage data on what legitimate scores look like.
- **Ask "how would we find out?" for every failure mode of every
  major dependency** (database, auth, rate limiter, external
  services). If the honest answer is "a user would tell us," that's
  a logging or monitoring gap — this is literally how the `/health`
  and logging findings were identified.
- **Periodically install and test in a clean environment, not just
  the one already sitting there.** Every PR in this review was
  verified with a fresh `venv`/`npm ci`, not the working directory's
  already-installed state — catches drift between what's committed
  and what actually reproducibly works from scratch.
- **When adopting new infrastructure, test its failure interactions
  with what already exists, not just its own happy path.** Alembic's
  own `fileConfig()` default silently broke unrelated logging;
  nothing about Alembic itself was broken, the *combination* was.
- **Confirm environment assumptions with whoever owns the actual
  deployment rather than guessing from the repo alone.** The
  rate-limiter fix took a different shape entirely once the actual
  Render start command was confirmed instead of assumed.

## Still open

- **Alembic production cutover** — `backend/alembic/README` has the
  exact steps (`alembic stamp head` on Render, then updating the
  start command); needs Render console access to finish.
- **GitHub branch protection** requiring CI to pass before merge —
  a repo settings change, not something a PR can do.
- **Marketing consent** — `LeaderboardEntry.vue` shows a static
  "by entering you agree..." notice, but the `marketing_consent`
  field and its checkbox are commented out in both the frontend and
  the backend schema, so there's no per-entrant record of what
  consent text they actually saw. Product/legal question, not an
  engineering one — flagged for whoever owns that decision.
- **Optional stretch items, not started**: disabling FastAPI's
  `/docs`/`/redoc` in production, and a Playwright end-to-end smoke
  test (play a round → submit → appears on the leaderboard) as a
  regression net beyond unit tests.
