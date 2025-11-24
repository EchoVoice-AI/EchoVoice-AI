"""Initial migration: create segments table.

Revision ID: 0001_create_segments
Revises: 
Create Date: 2025-11-24
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_segments'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'segmentmodel',
        sa.Column('id', sa.String(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Float(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('segmentmodel')
