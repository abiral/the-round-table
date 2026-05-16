#!/usr/bin/env bash
set -euo pipefail

# Run database migrations. Works both on the host (`bash backend/ops/migration.sh`)
# and inside the container (`docker compose exec backend bash ops/migration.sh`).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Load backend/.env when running on the host. Inside the container the env is
# already set by docker-compose, so this is a no-op when no .env is mounted.
if [ -f .env ]; then
  set -a; . .env; set +a
fi

uv run alembic upgrade head
