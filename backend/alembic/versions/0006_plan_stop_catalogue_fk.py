"""Point plan stops at the locked admin venue catalogue."""

from alembic import op
import sqlalchemy as sa

revision = "0006_plan_stop_catalogue_fk"
down_revision = "0005_canonical_collaboration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    constraints = inspector.get_foreign_keys("plan_stops")
    legacy = [constraint["name"] for constraint in constraints if constraint.get("name") and (constraint.get("name") == "plan_stops_ibfk_2" or constraint.get("referred_table") == "venues")]
    names = {item.get("name") for item in constraints}
    if legacy or "plan_stops_admin_venue_fk" not in names:
        with op.batch_alter_table("plan_stops", recreate="always") as batch:
            for name in legacy:
                batch.drop_constraint(name, type_="foreignkey")
            if "plan_stops_admin_venue_fk" not in names:
                batch.create_foreign_key("plan_stops_admin_venue_fk", "admin_venues", ["venue_id"], ["venue_id"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    names = {item.get("name") for item in inspector.get_foreign_keys("plan_stops")}
    with op.batch_alter_table("plan_stops", recreate="always") as batch:
        if "plan_stops_admin_venue_fk" in names:
            batch.drop_constraint("plan_stops_admin_venue_fk", type_="foreignkey")
        if "plan_stops_ibfk_2" not in names:
            batch.create_foreign_key("plan_stops_ibfk_2", "venues", ["venue_id"], ["id"])
