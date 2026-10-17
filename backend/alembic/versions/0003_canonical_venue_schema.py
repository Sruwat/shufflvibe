"""Create the normalized canonical venue tables for the MVP platform.

This migration is additive.  Google display-only fields are deliberately not
part of the schema; the app resolves them live from ``google_place_id``.
"""

from alembic import op

from app.venue_schema import DDL, INDEXES


revision = "0003_canonical_venue_schema"
down_revision = "0002_venue_platform"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for statement in DDL:
        op.execute(statement)
    for statement in INDEXES:
        # Index creation is best-effort for MySQL versions that do not accept
        # CREATE INDEX IF NOT EXISTS.  Table creation above is the contract.
        try:
            op.execute(statement)
        except Exception:
            pass


def downgrade() -> None:
    # This migration contains operational venue data.  Deliberately avoid a
    # destructive downgrade; restore from a database backup if required.
    pass
