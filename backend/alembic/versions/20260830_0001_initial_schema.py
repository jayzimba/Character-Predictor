"""Initial relational schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-30

The first revision builds tables from SQLAlchemy metadata so the models
remain the single source of truth. Later phases should add incremental
revisions instead of editing this file.
"""

from alembic import op

from app.database.base import Base
from app.models import *  # noqa: F403

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
