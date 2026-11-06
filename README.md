# Job Matcher

A resume/job matching demo app. Single user role — every logged-in user
(recruiter/admin) only ever sees and matches against their own job postings
and candidates. React + Vite + TypeScript frontend, Django REST Framework
backend, PostgreSQL + pgvector for embedding storage/search. No
Celery/Redis — there is no background work to run.

## AI layer: stub by default, real OpenAI optional

No OpenAI API key is required to run or test this app. `apps/common/ai.py`
switches purely on whether `OPENAI_API_KEY` is set in the environment:

- **Unset (default)**: `get_embedding()` returns a deterministic
  pseudo-random vector seeded from a sha256 hash of the input text - same
  text always produces the same vector, so the whole pipeline (store →
  search → rank) is reproducible and fully testable, but the vector carries
  **no real semantic meaning**. `generate_answer()` returns a fixed
  `[STUB AI RESPONSE ...]` string. The frontend shows a visible
  "running in stub mode" notice on the job detail page whenever this is
  active.
- **Set**: calls the real OpenAI embeddings API (model from
  `OPENAI_EMBEDDING_MODEL`, default `text-embedding-3-large`, shortened to
  `OPENAI_EMBEDDING_DIMENSIONS` dimensions) and chat completions API (model
  from `OPENAI_CHAT_MODEL`) for real match quality and real fit
  explanations.

## Vector storage: Postgres+pgvector, or SQLite for dev/test

`apps/common/embedding_field.py` and `apps/common/vector_search.py` pick the
storage/search strategy per backend, both behind the same function
signatures:

- **Postgres** (default/production): `pgvector.django.VectorField`, cosine
  similarity ranking via `pgvector.django.CosineDistance` in the database.
  Requires `CREATE EXTENSION vector`, handled automatically by the
  migration guard in `apps/common/migrations/0001_enable_pgvector.py`.
- **SQLite** (dev-only, `USE_SQLITE=True`): embeddings are stored as a plain
  `JSONField` (list of floats) and cosine similarity is computed in Python.
  **Never set `USE_SQLITE=True` in docker-compose or production** - it
  exists purely so `manage.py check/makemigrations/test` can run on a
  machine without Postgres/pgvector/Docker installed.

## Data model

- **User** — Django's `AbstractUser` with `email` as `USERNAME_FIELD`. This
  is the recruiter/admin account; Candidates and JobPostings are records it
  manages, not separate logins.
- **JobPosting** — `user`, `title`, `description`, `embedding` (of
  `title + "\n" + description`, recomputed on every save), `created_at`.
- **Candidate** — `user`, `name`, `email`, `resume_text`, `embedding` (of
  `resume_text`, recomputed on every save), `created_at`.

## REST API

- `POST /api/auth/register/`, `POST /api/auth/login/` (JWT),
  `POST /api/auth/refresh/`, `POST /api/auth/logout/`, `GET /api/auth/me/`
- `/api/jobs/` — list/create/retrieve/update/delete
- `GET /api/jobs/{id}/matches/?k=5` — ranks the requesting user's own
  candidates against this job's embedding (top-k), and generates a fit
  explanation for the single best match. Returns:
  ```json
  {
    "matches": [{"candidate_id": 1, "name": "Alice", "score": 0.83}],
    "top_match_explanation": "...",
    "stub_mode": true
  }
  ```
- `/api/candidates/` — list/create/retrieve/update/delete

Every ViewSet (and the matches action) scopes its queryset to
`request.user` — there is no cross-user access even by guessing another
user's object ID. See `apps/jobs/tests/test_matches.py` for the
cross-user-isolation tests covering jobs, candidates and the matches
endpoint together.

## Seed data

A data migration (`apps/candidates/migrations/0002_seed_demo_data.py`)
creates a demo account on first `migrate`:

- **Login**: `demo@example.com` / `demo12345`
- 5 realistic job postings (Backend Engineer, Data Analyst, Product
  Manager, Frontend Engineer, DevOps/SRE)
- 12 realistic candidates with varied skill sets
- Every row's embedding computed via `get_embedding()` at seed time (stub
  vectors, since no API key is configured in this environment)

The migration is idempotent — re-running `migrate` never creates
duplicates (it uses `get_or_create` for the user and checks for existing
rows before inserting jobs/candidates).

## Running locally with Docker (Postgres + pgvector)

```bash
cp .env.example .env
docker compose up --build
```

Backend on http://localhost:8000, frontend on http://localhost:5173.

## Running the backend without Docker (dev-only SQLite override)

No Postgres/pgvector/Docker needed for this - same `USE_SQLITE` pattern
used by the sibling apps in this workspace. **Never set `USE_SQLITE=True`
in docker-compose or production.**

```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash; use venv\Scripts\activate.bat on cmd

pip install -r requirements.txt

export USE_SQLITE=True
export DJANGO_SETTINGS_MODULE=config.settings.dev

python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Running the frontend

```bash
cd frontend
npm install
npm run dev      # dev server on :5173
npm run build    # production build (tsc -b && vite build)
```

Set `VITE_API_BASE_URL` if the backend isn't at `http://localhost:8000/api`.

## Auth trade-off (dev-only)

The access token is kept in memory only; the refresh token is kept in
`localStorage` and the client refreshes on a 401. A real deployment would
instead issue the refresh token as an httpOnly cookie from the backend -
this simplified pattern (same as the sibling apps in this workspace) is a
deliberate trade-off for a small demo app, not a recommendation for
production.

## What's NOT verified here

pgvector is not yet installed on the local Postgres in this environment, so
the Postgres code paths (`VectorField`, `CosineDistance`, the
`CREATE EXTENSION vector` migration guard) are written to be correct but
have only been exercised against SQLite here. Once pgvector is available:

```bash
cp .env.example .env   # with USE_SQLITE unset/False
docker compose up --build
docker compose exec backend python manage.py test
```

should be run to confirm the Postgres path end to end (the `migrate`
step will create the `vector` extension and the real `VectorField`
columns; `CosineDistance`-based ranking should be spot-checked against the
same known-vector test cases already covered on SQLite in
`apps/common/tests/test_vector_search.py`).
