"""users + pgcrypto + uuid_generate_v7

Revision ID: 001
Revises:
Create Date: 2026-05-16

"""
from typing import Sequence, Union

from alembic import op


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UUID_V7_FN = """
CREATE OR REPLACE FUNCTION uuid_generate_v7()
RETURNS uuid
LANGUAGE plpgsql
VOLATILE
AS $$
DECLARE
  unix_ts_ms bigint;
  uuid_bytes bytea;
BEGIN
  unix_ts_ms := (extract(epoch from clock_timestamp()) * 1000)::bigint;
  -- 16 random bytes, then overlay the high 6 bytes with the timestamp.
  uuid_bytes := overlay(
    gen_random_bytes(16)
    placing substring(int8send(unix_ts_ms) from 3 for 6)
    from 1 for 6
  );
  -- Version 7 in the high nibble of byte 6.
  uuid_bytes := set_byte(uuid_bytes, 6, ((get_byte(uuid_bytes, 6) & 15) | 112));
  -- RFC 4122 variant (high two bits of byte 8 set to 10).
  uuid_bytes := set_byte(uuid_bytes, 8, ((get_byte(uuid_bytes, 8) & 63) | 128));
  RETURN encode(uuid_bytes, 'hex')::uuid;
END;
$$;
"""


def upgrade() -> None:
    # pgcrypto provides crypt(), gen_salt(), and gen_random_bytes() (used by
    # uuid_generate_v7). It is idempotent across migrations.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.execute(UUID_V7_FN)

    op.execute(
        """
        CREATE TABLE users (
          id          UUID         PRIMARY KEY DEFAULT uuid_generate_v7(),
          firstname   TEXT         NOT NULL,
          lastname    TEXT         NOT NULL,
          email       TEXT         NOT NULL UNIQUE,
          password    TEXT         NOT NULL,
          created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
          updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
        );
        """
    )
    op.execute("CREATE INDEX users_email_lower_idx ON users (lower(email));")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS users_email_lower_idx;")
    op.execute("DROP TABLE IF EXISTS users;")
    op.execute("DROP FUNCTION IF EXISTS uuid_generate_v7();")
    # pgcrypto extension is intentionally left in place.
