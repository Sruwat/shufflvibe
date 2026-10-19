"""Canonical MVP friendship, gathering and wheel state.

The migration makes the social planning flow durable instead of storing it in
room/capsule metadata JSON. It is deliberately additive so existing rooms,
plans and conversations remain readable while the frontend migrates.
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_canonical_mvp_gatherings"
down_revision = "0006_plan_stop_catalogue_fk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing = set(inspector.get_table_names())
    if "friendships" not in existing:
        op.create_table(
        "friendships",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("requester_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("addressee_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
        )
    if "gatherings" not in existing:
        op.create_table(
        "gatherings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="gathering"),
        sa.Column("wheel_owner_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
    if "gathering_members" not in existing:
        op.create_table(
        "gathering_members",
        sa.Column("gathering_id", sa.String(36), sa.ForeignKey("gatherings.id"), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role", sa.String(24), nullable=False, server_default="member"),
        sa.Column("invite_status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("skeleton", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("joined_at", sa.DateTime(timezone=True)),
        )
    if "wheel_requests" not in existing:
        op.create_table(
        "wheel_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("gathering_id", sa.String(36), sa.ForeignKey("gatherings.id"), nullable=False),
        sa.Column("requester_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
    if "gathering_proposals" not in existing:
        op.create_table(
        "gathering_proposals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("gathering_id", sa.String(36), sa.ForeignKey("gatherings.id"), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    op.drop_table("gathering_proposals")
    op.drop_table("wheel_requests")
    op.drop_table("gathering_members")
    op.drop_table("gatherings")
    op.drop_table("friendships")
