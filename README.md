# Construction Projects API

A FastAPI-based backend service for listing construction projects with area-based filtering, built with modern Python practices and RFC 9457 compliant error handling.

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd construction-api
uv sync --group dev

# Run the development server
uv run fastapi dev src/construction_api/main.py
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [API Endpoints](#api-endpoints)
- [Example Requests](#example-requests)
- [Error Handling](#error-handling)
- [Assumptions](#assumptions)
- [Trade-offs & Limitations](#trade-offs--limitations)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## Features

- **Area-based Filtering**: Search projects by area with case-insensitive partial matching
- **Pagination**: 1-based page/per_page pagination for efficient data retrieval
- **RFC 9457 Errors**: Standardized error response format
- **SQLite Database**: Lightweight, file-based database
- **Comprehensive Tests**: Full test coverage with pytest
- **Modern Python**: Python 3.13+ with type hints
- **Auto-formatting**: Ruff for linting and formatting

---

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd construction-api
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync --group dev
   ```

   Or with pip:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   pip install -e ".[dev]"
   ```

3. **Set up the database:**
   ```bash
   # Copy the example database file
   cp data/construction.db.example data/construction.db
   ```
   
   > **Note:** The `data/construction.db.example` file is a sample database that you can use as a starting point. Copy it to `data/construction.db` to get started quickly.

---

## Running Locally

### Development Server (with hot reload)

```bash
uv run fastapi dev src/construction_api/main.py
```

### Production Server

```bash
uv run uvicorn src.construction_api.main:app --host 0.0.0.0 --port 8000
```

### Access Points

| Service                       | URL                              |
|-------------------------------|----------------------------------|
| API                           | `http://localhost:8000`          |
| Swagger UI (Interactive Docs) | `http://localhost:8000/docs`     |

---

## API Endpoints

### List Projects by Area

```
GET /api/v1/projects
```

**Query Parameters:**

| Parameter  | Type    | Required | Default | Description                                      |
|------------|---------|----------|---------|--------------------------------------------------|
| `area`     | string  | Yes      | -       | Filter by area (case-insensitive, partial match) |
| `page`     | integer | No       | 1       | Page number (1-based)                            |
| `per_page` | integer | No       | 10      | Items per page (min: 1)                          |

**Example:**
```bash
GET /api/v1/projects?area=London&page=1&per_page=10
```

### Get Project by ID

```
GET /api/v1/projects/{project_id}
```

**Path Parameters:**

| Parameter    | Type   | Description                   |
|--------------|--------|-------------------------------|
| `project_id` | string | Project ID (e.g., `p-000001`) |

### Get Project Areas

```
GET /api/v1/projects/{project_id}/areas
```

Returns all areas associated with a specific project.

---

## Example Requests

### 1. List Projects in London

**Request:**
```bash
curl "http://localhost:8000/api/v1/projects?area=London"
```

**Response (200 OK):**
```json
{
  "area": "Leeds",
  "page": 1,
  "per_page": 10,
  "total": 180,
  "projects": [
    {
      "id": "p-000181",
      "project_name": "Leeds Road Expansion Upgrade",
      "project_start": "2025-08-06 00:00:00",
      "project_end": "2025-12-29 00:00:00",
      "company": "NorthBuild Ltd",
      "description": "Infrastructure upgrade in Leeds with phased delivery.",
      "project_value": 5529189,
      "areas": ["Leeds"]
    }
  ]
}
```

### 2. Partial Match Search

**Request:**
```bash
curl "http://localhost:8000/api/v1/projects?area=lee"
```

Matches: Leeds, Lee, Littleborough, etc.

**Response:**
```json
{
  "area": "Leeds",
  "page": 1,
  "per_page": 10,
  "total": 180,
  "projects": [...]
}
```

### 3. Get Project by ID

**Request:**
```bash
curl "http://localhost:8000/api/v1/projects/p-000001"
```

**Response (200 OK):**
```json
{
  "id": "p-000001",
  "project_name": "Manchester Bridge Phase 2",
  "project_start": "2025-05-16 00:00:00",
  "project_end": "2026-02-28 00:00:00",
  "company": "NorthBuild Ltd",
  "description": "Major road expansion project...",
  "project_value": 4832115,
  "areas": ["Manchester"]
}
```

### 4. Get Project Areas

**Request:**
```bash
curl "http://localhost:8000/api/v1/projects/p-000001/areas"
```

**Response (200 OK):**
```json
{
  "project_id": "p-000001",
  "project_name": "Manchester Bridge Phase 2",
  "areas": ["Manchester"]
}
```

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

## Assumptions

1. **Area-based filtering** is the primary use case for searching projects.
2. **Read-only API** - focuses on listing/retrieving projects, not CRUD operations.
3. **SQLite database** is sufficient for this use case; production would use PostgreSQL.
4. **Project IDs are strings** (e.g., `p-000001`) not integers.
5. **Case-insensitive area matching** with partial match support (LIKE query).
6. **Projects can have multiple areas** via a many-to-many relationship.

---

## Trade-offs & Limitations

### Current Implementation

| Aspect           | Decision                     | Trade-off                                                                     |
|------------------|------------------------------|-------------------------------------------------------------------------------|
| **Database**     | SQLite                       | ✅ Simple setup, no server needed<br>❌ Not suitable for high concurrency       |
| **Pagination**   | Page-based (1-based)         | ✅ User-friendly API<br>❌ Less efficient than cursor-based for deep pagination |
| **Area Search**  | Case-insensitive LIKE        | ✅ Flexible search<br>❌ Slower on large datasets (no index usage)              |
| **Error Format** | RFC 9457                     | ✅ Standard format<br>❌ More verbose than simple `{detail}`                    |
| **Architecture** | Hexagonal (Ports & Adapters) | ✅ Clean separation, testable<br>❌ More boilerplate code                       |

### Known Limitations

1. **No Authentication**: API is open; no rate limiting or API keys.
2. **No Write Operations**: Cannot create, update, or delete projects.
3. **Limited Filtering**: Only area-based filtering; no date filters, budget filter, or status filters.
4. **SQLite Concurrency**: Not suitable for high-traffic production use.
5. **No Caching**: Every request hits the database.

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
├── .ruff.toml                  # Ruff configuration
└── README.md                   # This file
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

This project is created for learning purposes
