#!/usr/bin/env bash
set -euo pipefail

# Onboard a new user. Interactive by default; argv-driven if all flags given:
#   bash backend/ops/onboard.sh --firstname X --lastname Y --email z@a.com
# Password is always read via getpass (never on the command line).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ -f .env ]; then
  set -a; . .env; set +a
fi

uv run python ops/onboard.py "$@"
