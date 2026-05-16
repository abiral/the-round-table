"""Admin user onboarding CLI.

Prompts (or accepts via argv) for firstname / lastname / email / password, then
inserts the user into the `users` table. Password is hashed in Postgres via
`crypt(:password, gen_salt('bf'))`. The plaintext never touches the application
beyond the SQL parameter binding.

Usage:
    bash backend/ops/onboard.sh
    bash backend/ops/onboard.sh --firstname Abiral --lastname Rai --email a@b.com
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from getpass import getpass
from pathlib import Path

# Make `import app.*` work whether the script is invoked from backend/ or elsewhere.
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from dotenv import load_dotenv  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.exc import IntegrityError  # noqa: E402

load_dotenv()

# Imported after load_dotenv so DATABASE_URL is in env before the engine is built.
from app.db.session import async_session_maker  # noqa: E402


def _prompt(label: str, supplied: str | None) -> str:
    if supplied:
        return supplied.strip()
    value = input(f"{label}: ").strip()
    if not value:
        print(f"{label} is required.", file=sys.stderr)
        sys.exit(2)
    return value


async def onboard(firstname: str, lastname: str, email: str, password: str) -> None:
    async with async_session_maker() as session:
        existing = (
            await session.execute(
                text("SELECT id FROM users WHERE lower(email) = lower(:email)"),
                {"email": email},
            )
        ).first()
        if existing:
            print(f"A user with email {email!r} already exists.", file=sys.stderr)
            sys.exit(1)

        try:
            row = (
                await session.execute(
                    text(
                        """
                        INSERT INTO users (firstname, lastname, email, password)
                        VALUES (:firstname, :lastname, lower(:email), crypt(:password, gen_salt('bf')))
                        RETURNING id
                        """
                    ),
                    {
                        "firstname": firstname,
                        "lastname": lastname,
                        "email": email,
                        "password": password,
                    },
                )
            ).mappings().first()
            await session.commit()
        except IntegrityError:
            await session.rollback()
            print(f"A user with email {email!r} already exists.", file=sys.stderr)
            sys.exit(1)

        assert row is not None
        print(f"Onboarded {email}  (id={row['id']})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Onboard a new user.")
    parser.add_argument("--firstname")
    parser.add_argument("--lastname")
    parser.add_argument("--email")
    args = parser.parse_args()

    firstname = _prompt("First name", args.firstname)
    lastname = _prompt("Last name", args.lastname)
    email = _prompt("Email", args.email)

    password = getpass("Password: ")
    if not password:
        print("Password is required.", file=sys.stderr)
        sys.exit(2)
    confirm = getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        sys.exit(2)

    asyncio.run(onboard(firstname, lastname, email, password))


if __name__ == "__main__":
    main()
