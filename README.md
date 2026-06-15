# EzExpense

A lightweight, mobile-first personal expense tracking web app. Track spending, categorize transactions, and visualize financial habits — all from your phone browser.

## Features

- **Quick expense logging** — amount, category, tags, notes, and timestamp
- **Custom categories & tags** — 8 preset categories on signup, fully customizable
- **Category-tag linkage** — tags auto-filter by selected category based on historical records
- **Smart search** — keyword search across notes, amounts, categories, and tags
- **Multi-dimensional statistics** — pie charts (by category/tag), bar charts (monthly trends), with flexible time range filtering
- **Time-based filtering** — expense list supports month/quarter/year/custom time range
- **Trash & restore** — soft delete with one-click recovery, batch permanent delete
- **PWA support** — add to home screen, standalone display
- **Multi-user** — isolated accounts with JWT authentication

## Tech Stack

| Layer | Stack |
|-------|-------|
| Backend | Python 3.11+ / FastAPI / SQLAlchemy 2.0 (async) / SQLite / Alembic |
| Frontend | Vue 3 / TypeScript / Vite 8 / Vant 4 / Pinia / ECharts 6 |
| Auth | JWT (HS256) + bcrypt |
| Deploy | Docker multi-stage build |

## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

Open `http://localhost:8080` on your phone.

### Manual

**Backend:**

```bash
cd backend
uv venv
uv pip install -r requirements.txt
.venv/bin/python main.py
```

**Frontend:**

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173` (dev) or `http://localhost:8080` (production).

## Development

### Run tests

```bash
# Backend unit tests
cd backend
.venv/bin/python -m pytest test_catalog_core.py test_soft_delete.py test_statistics.py -v

# Backend integration tests (requires running server)
.venv/bin/python -m pytest test_api.py -v

# Frontend tests
cd frontend
npx vitest

# E2E tests (requires Playwright browsers installed once)
cd e2e
npm install
npx playwright install --with-deps chromium webkit  # first time only
npm test
```

### Database migrations

```bash
cd backend
.venv/bin/python -m alembic upgrade head          # apply migrations
.venv/bin/python -m alembic revision --autogenerate -m "desc"  # create migration
```

## Project Structure

```
backend/
  api/           # FastAPI route handlers
  services/      # Business logic
  models/        # SQLAlchemy ORM models
  schemas/       # Pydantic request/response models
  middleware/    # JWT auth + error handling
frontend/
  src/
    views/       # Page components
    stores/      # Pinia state management
    components/  # Shared UI components
    composables/ # Vue composables (charts, filters)
    lib/         # HTTP client, token, notifications
    core/        # Pure utility functions (format, time)
    styles/      # Design tokens (tokens.css) + global CSS overrides (global.css)
e2e/
  playwright.config.ts  # Playwright config (webServer, devices, projects)
  global-setup.ts       # Test data seeding + auth state
  fixtures/             # Custom test fixtures
  helpers/              # Gesture helpers, API client
  tests/                # 12 spec files: S1 auth, S2 expense CRUD, S3 form interactions, S4 statistics, S5 pull-refresh & tabbar, S6 category manage, S7 tag manage, S8 navigation stability, S9 form optimization, S10 category-tag linkage, S11 list filter, S12 trash batch delete
```

## Configuration

Backend config via `backend/config.yaml`, overridable with environment variables:

```bash
APP_SERVER_PORT=9090
APP_DATABASE_PATH=/data/my_expense.db
APP_SECURITY_JWT_SECRET=your-secret-key
```

## Deployment

Production builds serve the frontend from FastAPI. CI auto-publishes Docker images to GHCR on version tags (`v*`).

```bash
# Build and push
git tag v1.0.0
git push origin v1.0.0
```

## License

Private project.
