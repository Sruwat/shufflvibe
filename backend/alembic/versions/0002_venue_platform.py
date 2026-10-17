"""Add the canonical venue lifecycle, provenance, media and pipeline tables.

This migration is additive. Existing ``admin_venues`` rows remain intact and
are backfilled into the new lifecycle columns by the application bootstrap.
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_venue_platform"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    # ``admin_venues`` is maintained by the dashboard bootstrap on existing
    # installs, but Alembic must also work from a clean database.
    if "admin_venues" not in inspector.get_table_names():
        op.create_table(
            "admin_venues",
            sa.Column("venue_id", sa.String(180), primary_key=True),
            sa.Column("google_place_id", sa.String(180), unique=True),
            sa.Column("display_name", sa.String(255), nullable=False, server_default=""),
            sa.Column("city", sa.String(120), nullable=False, server_default=""),
            sa.Column("state", sa.String(120), nullable=False, server_default="Delhi"),
            sa.Column("area", sa.String(160), nullable=False, server_default=""),
            sa.Column("admission_status", sa.String(40), nullable=False, server_default="Insufficient evidence"),
            sa.Column("verification_status", sa.String(40), nullable=False, server_default="in_process"),
            sa.Column("official_url", sa.Text()),
            sa.Column("google_lookup_url", sa.Text()),
            sa.Column("data_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("source_synced_at", sa.String(40)),
            sa.Column("updated_at", sa.String(40), nullable=False, server_default=""),
            if_not_exists=True,
        )
        inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("admin_venues")} if "admin_venues" in inspector.get_table_names() else set()
    if "eligibility_status" not in columns:
        op.add_column("admin_venues", sa.Column("eligibility_status", sa.String(40), nullable=False, server_default="NEEDS_REVIEW"))
    if "publication_status" not in columns:
        op.add_column("admin_venues", sa.Column("publication_status", sa.String(40), nullable=False, server_default="DRAFT"))

    op.create_table(
        "venue_publication_versions",
        sa.Column("version_id", sa.String(64), primary_key=True),
        sa.Column("venue_id", sa.String(180), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(180), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.UniqueConstraint("venue_id", "version_number"),
        if_not_exists=True,
    )
    op.create_table(
        "venue_manual_overrides",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("venue_id", sa.String(180), nullable=False),
        sa.Column("field_name", sa.String(120), nullable=False),
        sa.Column("automatic_value", sa.Text()),
        sa.Column("manual_value", sa.Text()),
        sa.Column("effective_value", sa.Text()),
        sa.Column("reason", sa.Text()),
        sa.Column("edited_by", sa.String(180), nullable=False),
        sa.Column("edited_at", sa.String(40), nullable=False),
        sa.Column("reset_at", sa.String(40)),
        if_not_exists=True,
    )
    op.create_table(
        "venue_change_history",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("venue_id", sa.String(180), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("before_json", sa.Text()),
        sa.Column("after_json", sa.Text()),
        sa.Column("actor", sa.String(180), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        if_not_exists=True,
    )
    op.create_table(
        "venue_pipeline_runs",
        sa.Column("run_id", sa.String(64), primary_key=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("source_dir", sa.Text()),
        sa.Column("source_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.String(40), nullable=False),
        sa.Column("finished_at", sa.String(40)),
        sa.Column("summary_json", sa.Text()),
        if_not_exists=True,
    )
    op.create_table(
        "venue_media",
        sa.Column("media_id", sa.String(64), primary_key=True),
        sa.Column("venue_id", sa.String(180), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("media_type", sa.String(40), nullable=False, server_default="image"),
        sa.Column("source_type", sa.String(40), nullable=False, server_default="admin_upload"),
        sa.Column("rights_status", sa.String(80), nullable=False, server_default="unknown"),
        sa.Column("alt_text", sa.String(255), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_cover", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_by", sa.String(180), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        if_not_exists=True,
    )
    media_columns = {column["name"] for column in sa.inspect(bind).get_columns("venue_media")}
    if "crop_json" not in media_columns:
        op.add_column("venue_media", sa.Column("crop_json", sa.Text()))
    if "variants_json" not in media_columns:
        op.add_column("venue_media", sa.Column("variants_json", sa.Text()))


def downgrade() -> None:
    # Deliberately leave data-bearing tables in place; rollback is performed by
    # restoring the pre-migration database backup, not by destructive drops.
    pass
