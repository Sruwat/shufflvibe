from sqlalchemy import create_engine

from backend.app.state_store import RuntimeStateStore


def test_normalized_domain_tables_are_created_by_admin_store():
    from sqlalchemy import inspect
    from backend.app.admin_store import store

    tables = set(inspect(store.engine).get_table_names())
    assert {"users", "profiles", "plans", "plan_stops", "rooms", "messages", "notifications", "reports"}.issubset(tables)


def test_runtime_state_survives_store_recreation(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'state.db'}", future=True)
    first = RuntimeStateStore(engine)
    first.save("rooms", [{"id": "room-1", "status": "draft"}])

    second = RuntimeStateStore(engine)
    assert second.load("rooms") == [{"id": "room-1", "status": "draft"}]
