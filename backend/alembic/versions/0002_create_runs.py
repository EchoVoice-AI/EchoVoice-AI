"""Create runs table for persisted run metadata.

Revision ID: 0002_create_runs
Revises: 0001_create_segments
Create Date: 2025-11-25
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '0002_create_runs'
down_revision = '0001_create_segments'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the `runmodel` table for persisted run metadata if missing.

    The migration is idempotent and will skip creation when the table
    already exists (useful for local development or when the table was
    created out-of-band).
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if not inspector.has_table('runmodel'):
        op.create_table(
            'runmodel',
            sa.Column('id', sa.String(), primary_key=True, nullable=False),
            sa.Column('status', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.Column('payload', sa.JSON(), nullable=True),
            sa.Column('result', sa.JSON(), nullable=True),
            sa.Column('logs', sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    """Drop the `runmodel` table created in the upgrade step."""
    op.drop_table('runmodel')
