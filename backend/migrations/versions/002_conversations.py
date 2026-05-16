"""conversations table

Revision ID: 002
Revises: 001
Create Date: 2026-05-16

"""
from typing import Sequence, Union

from alembic import op


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE conversations (
          id               UUID         PRIMARY KEY DEFAULT uuid_generate_v7(),
          user_id          UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          title            TEXT         NOT NULL DEFAULT '',
          status           TEXT         NOT NULL DEFAULT 'in_progress'
                                        CHECK (status IN ('in_progress', 'awaiting_user', 'concluded')),
          state            JSONB        NOT NULL,
          last_message_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
          created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
          updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        "CREATE INDEX conversations_user_recent_idx "
        "ON conversations (user_id, last_message_at DESC);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS conversations_user_recent_idx;")
    op.execute("DROP TABLE IF EXISTS conversations;")
