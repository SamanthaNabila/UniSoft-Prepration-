# syntax=docker/dockerfile:1
# UniDesk public demo — single image: FastAPI serves the built React SPA + the API.
# Build context is the UniDesk/ directory.

# ---------- stage 1: build the React frontend ----------
FROM node:22-alpine AS frontend
WORKDIR /fe

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
# Same-origin API in the deployed image. Local `npm run dev` is unaffected
# (it never sees this env var).
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build          # -> /fe/dist

# ---------- stage 2: python runtime ----------
FROM python:3.13-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend /fe/dist ./static

EXPOSE 8000

# Migrate (Postgres), seed demo data once (idempotent), then serve.
CMD ["sh", "-c", "alembic upgrade head && python scripts/seed_demo.py && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
