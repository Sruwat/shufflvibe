import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.models import Base

config = context.config
target_metadata = Base.metadata


def load_database_url() -> None:
    for raw_line in (Path(__file__).resolve().parents[1] / '.env').read_text(encoding='utf-8').splitlines() if (Path(__file__).resolve().parents[1] / '.env').exists() else []:
        line = raw_line.strip()
        if line.startswith('DATABASE_URL=') and 'DATABASE_URL' not in os.environ:
            os.environ['DATABASE_URL'] = line.split('=', 1)[1].strip().strip('"').strip("'")
    url = os.getenv('DATABASE_URL', '').strip()
    if url:
        config.set_main_option('sqlalchemy.url', url.replace('%', '%%'))


load_database_url()

def run_migrations_offline():
    context.configure(url=config.get_main_option('sqlalchemy.url'), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction(): context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix='sqlalchemy.', poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction(): context.run_migrations()

if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
