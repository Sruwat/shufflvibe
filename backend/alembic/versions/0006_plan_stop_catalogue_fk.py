"""Point plan stops at the locked admin venue catalogue.

The public venue API uses ``admin_venues.venue_id`` (the stable catalogue
identifier).  The original ORM model referenced the unused legacy ``venues``
table, which made a real MySQL plan fail as soon as a published venue was
selected.
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_plan_stop_catalogue_fk"
down_revision = "0005_canonical_collaboration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    constraints = inspector.get_foreign_keys("plan_stops")
    for constraint in constraints:
        if constraint.get("name") == "plan_stops_ibfk_2" or constraint.get("referred_table") == "venues":
            op.drop_constraint(constraint["name"], "plan_stops", type_="foreignkey")
    names = {item.get("name") for item in inspector.get_foreign_keys("plan_stops")}
    if "plan_stops_admin_venue_fk" not in names:
        op.create_foreign_key(
            "plan_stops_admin_venue_fk",
            "plan_stops",
            "admin_venues",
            ["venue_id"],
            ["venue_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    names = {item.get("name") for item in inspector.get_foreign_keys("plan_stops")}
    if "plan_stops_admin_venue_fk" in names:
        op.drop_constraint("plan_stops_admin_venue_fk", "plan_stops", type_="foreignkey")
    if not any(item.get("name") == "plan_stops_ibfk_2" for item in inspector.get_foreign_keys("plan_stops")):
        op.create_foreign_key("plan_stops_ibfk_2", "plan_stops", "venues", ["venue_id"], ["id"])
