"""Add canonical room collaboration and per-user receipt tables.

All tables are additive and contain user-owned application state only. Google
display-time enrichment is intentionally excluded.
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_canonical_collaboration"
down_revision = "0004_nullable_score_values"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "room_members",
        sa.Column("room_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(180), nullable=False),
        sa.Column("role", sa.String(24), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.String(40), nullable=False),
        sa.PrimaryKeyConstraint("room_id", "user_id"),
        if_not_exists=True,
    )
    op.create_table(
        "room_invites",
        sa.Column("invite_id", sa.String(64), primary_key=True),
        sa.Column("room_id", sa.String(36), nullable=False),
        sa.Column("invite_token", sa.String(180), nullable=False, unique=True),
        sa.Column("created_by", sa.String(180), nullable=False),
        sa.Column("expires_at", sa.String(40)),
        sa.Column("used_by", sa.String(180)),
        sa.Column("created_at", sa.String(40), nullable=False),
        if_not_exists=True,
    )
    op.create_table(
        "message_receipts",
        sa.Column("message_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(180), nullable=False),
        sa.Column("read_at", sa.String(40), nullable=False),
        sa.PrimaryKeyConstraint("message_id", "user_id"),
        if_not_exists=True,
    )
    op.create_table(
        "notification_reads",
        sa.Column("notification_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(180), nullable=False),
        sa.Column("read_at", sa.String(40), nullable=False),
        sa.PrimaryKeyConstraint("notification_id", "user_id"),
        if_not_exists=True,
    )
    op.create_table(
        "capsules_members",
        sa.Column("capsule_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(180), nullable=False),
        sa.Column("approved", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("capsule_id", "user_id"),
        if_not_exists=True,
    )


def downgrade() -> None:
    # Data-bearing collaboration tables are intentionally retained. Restore a
    # database backup for rollback rather than destructively dropping state.
    pass
