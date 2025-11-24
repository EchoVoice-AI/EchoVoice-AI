"""Alembic environment for EchoVoice-AI backend migrations.

This env.py sets up SQLAlchemy/SQLModel metadata from `api.db` so that
`alembic revision --autogenerate` can detect model changes.
"""
from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
try:
    # Attempt to configure logging from the alembic.ini file. If the
    # file does not contain the expected logger sections, fall back to a
    # simple basicConfig to avoid crashing during env import.
    fileConfig(config.config_file_name)
except Exception:
    import logging

    logging.basicConfig(level=logging.INFO)

# Import your model's MetaData object here
try:
    from api import db as models_db
    target_metadata = models_db.SQLModel.metadata
except Exception:
    target_metadata = None


def get_url() -> str | None:
    """Return the database URL from environment or alembic.ini.

    Prefer the `DATABASE_URL` environment variable for safety.
    """
    return os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")


def run_migrations_offline():
    """Run migrations in 'offline' mode (SQL script output).

    This configuration is useful for generating SQL without connecting
    to the database.
    """
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode (apply to DB).

    Creates an Engine and a connection and runs migrations against it.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration = dict(configuration) if configuration else {}
    url = get_url()
    if url:
        configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
