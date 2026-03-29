# Construction Projects API — Detailed Documentation

## Features

- **Area-based Filtering**: Search projects by area with case-insensitive partial matching
- **Sorting**: Projects sorted by value (highest first), then name (A–Z)
- **Pagination**: 1-based page/per_page pagination for efficient data retrieval
- **RFC 9457 Errors**: Standardized error response format
- **SQLite Database**: Lightweight, file-based database
- **Comprehensive Tests**: Full test coverage with pytest
- **Modern Python**: Python 3.13+ with type hints
- **Auto-formatting**: Ruff for linting and formatting

---

## API Endpoints

### List Projects by Area

```
GET /projects
GET /api/v1/projects
```

> Both paths serve the same endpoint. `/api/v1/projects` is the versioned canonical path.

**Query Parameters:**

| Parameter  | Type    | Required | Default | Description                                      |
|------------|---------|----------|---------|--------------------------------------------------|
| `area`     | string  | Yes      | -       | Filter by area (case-insensitive, partial match) |
| `page`     | integer | No       | 1       | Page number (1-based)                            |
| `per_page` | integer | No       | 10      | Items per page (min: 1)                          |

### Get Project by ID

```
GET /api/v1/projects/{project_id}
```

| Parameter    | Type   | Description                   |
|--------------|--------|-------------------------------|
| `project_id` | string | Project ID (e.g., `p-000001`) |

### Get Project Areas

```
GET /api/v1/projects/{project_id}/areas
```

Returns all areas associated with a specific project.

---

## Error Handling

All errors follow **RFC 9457** (Problem Details for HTTP APIs) format.

### Validation Error (422)

```json
{
  "title": "Request Validation Error",
  "status": 422,
  "detail": "query -> area: Field required",
  "instance": "/api/v1/projects"
}
```

### Not Found Error (404)

```json
{
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Project not found",
  "instance": "/api/v1/projects/p-999999"
}
```

### Internal Server Error (500)

```json
{
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred. Please try again later.",
  "instance": "/api/v1/projects"
}
```

---

## Testing

### Run All Tests

```bash
uv run pytest
```

### Run with Coverage

```bash
uv run pytest --cov=src/construction_api --cov-report=html
```

### Run Specific Test File

```bash
uv run pytest tests/test_projects.py -v
```

### Linting & Formatting

```bash
# Check code style
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check src/ tests/ --fix

# Format code
uv run ruff format src/ tests/
```

---

## Project Structure

```
construction-api/
├── src/construction_api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app & exception handlers
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic response schemas
│   ├── ports.py                # Contains interfaces (Hexagonal)
│   ├── adapters.py             # Contains implementations
│   ├── services.py             # Business logic layer
│   ├── dependencies.py         # Dependency injection container
│   ├── error_handlers.py       # RFC 9457 error handling
│   └── routes/v1/
│       └── projects.py         # API endpoints
├── tests/
│   ├── conftest.py             # Test fixtures & config
│   └── test_projects.py        # Endpoint tests
├── data/
│   ├── construction.db.example # Example database (tracked in git)
│   └── construction.db         # SQLite database (gitignored)
├── pyproject.toml              # Dependencies & config
├── uv.lock                     # Locked dependencies
└── README.md
```

---

## Technology Stack

| Component           | Technology                 |
|---------------------|----------------------------|
| **Framework**       | FastAPI 0.135.2            |
| **Database**        | SQLite / SQLAlchemy 2.0.48 |
| **Validation**      | Pydantic 2.12.5            |
| **Server**          | Uvicorn 0.42.0             |
| **Testing**         | pytest 9.0.2               |
| **Linting**         | Ruff 0.15.8                |
| **Package Manager** | uv                         |

---

## License

This project is created for learning purposes.
