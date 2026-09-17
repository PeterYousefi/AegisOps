#!/usr/bin/env bash
# AegisOps local launcher.
# Starts PostgreSQL (Homebrew), the FastAPI backend, and the Next.js frontend,
# then opens the app. Ctrl-C stops the backend and frontend.
#
# Usage:  ./run.sh
#
# Requirements: Homebrew postgresql@16, Python 3.12 venv in backend/.venv,
# and frontend deps installed (npm install).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export POSTGRES_USER="${POSTGRES_USER:-aegisops}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-local-dev-only}"
export POSTGRES_DB="${POSTGRES_DB:-aegisops}"
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"

PGBIN="/opt/homebrew/opt/postgresql@16/bin"

echo "==> Ensuring PostgreSQL is running..."
if ! "$PGBIN/pg_isready" -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" >/dev/null 2>&1; then
  brew services start postgresql@16 || true
  sleep 3
fi

echo "==> Ensuring role/database exist..."
"$PGBIN/psql" -d postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'" \
  | grep -q 1 || "$PGBIN/psql" -d postgres -c \
  "CREATE ROLE ${POSTGRES_USER} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}' CREATEDB;"
"$PGBIN/psql" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'" \
  | grep -q 1 || "$PGBIN/createdb" -O "${POSTGRES_USER}" "${POSTGRES_DB}"

echo "==> Applying migrations and seeding..."
cd "$ROOT/backend"
.venv/bin/alembic upgrade head
.venv/bin/python -m seed.seed_data

echo "==> Starting backend on http://localhost:8000 ..."
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "==> Starting frontend on http://localhost:3000 ..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

cleanup() {
  echo ""
  echo "==> Stopping..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

sleep 4
echo ""
echo "AegisOps is starting. Open http://localhost:3000"
echo "Press Ctrl-C to stop."
wait
