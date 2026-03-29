# Construction Projects API

A FastAPI backend for listing construction projects with area-based filtering.

## Running Locally

**Prerequisites:** Python 3.13+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/tonidy/construction-api.git
cd construction-api
uv sync --group dev
cp data/construction.db.example data/construction.db
uv run fastapi dev src/construction_api/main.py
```

API: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

## Example Requests

```bash
# List projects by area (required param, partial match, case-insensitive)
curl "http://localhost:8000/api/v1/projects?area=Leeds"

# With pagination
curl "http://localhost:8000/api/v1/projects?area=Leeds&page=2&per_page=5"

# Get a single project
curl "http://localhost:8000/api/v1/projects/p-000001"

# Get areas for a project
curl "http://localhost:8000/api/v1/projects/p-000001/areas"
```

## Assumptions

1. **Read-only API** — focuses on listing/retrieving projects, not CRUD operations.
2. **SQLite** is sufficient for this use case; production would use PostgreSQL.
3. **Case-insensitive partial matching** for area filtering (SQL LIKE).
4. **Project IDs are strings** (e.g., `p-000001`), not integers.
5. **Projects can belong to multiple areas** via a many-to-many relationship.

## Trade-offs & Limitations

- **SQLite** — simple setup, but not suitable for high concurrency.
- **Page-based pagination** — user-friendly, but less efficient than cursor-based for deep pages.
- **No authentication** — no rate limiting or API keys.
- **No caching** — every request hits the database.
- **Limited filtering** — area only; no date, budget, or status filters.
- **RFC 9457 errors** — standards-compliant but more verbose than simple `{"detail": "..."}`.

---

For full API reference, project structure, testing, and tech stack details see [DOCS.md](DOCS.md).
