"""Allow explicit not_specialised score rows to have no numeric score."""

from alembic import op
import sqlalchemy as sa

revision = "0004_nullable_score_values"
down_revision = "0003_canonical_venue_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "mysql":
        op.alter_column("venue_scores", "score", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "mysql":
        op.alter_column("venue_scores", "score", existing_type=sa.Integer(), nullable=False)
