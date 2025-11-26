"""Create generator, retriever, delivery and hitl rule tables.

Revision ID: 0003_create_generator_retriever_delivery
Revises: 0002_create_runs
Create Date: 2025-11-26
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '0003_gen_retr_del'
down_revision = '0002_create_runs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables for generators, retrievers, delivery channels, and HITL rules.

    This migration is idempotent and will skip creation if a table already
    exists (useful for local development where tables may be created
    out-of-band by the application).
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not inspector.has_table('generatormodel'):
        op.create_table(
            'generatormodel',
            sa.Column('id', sa.String(), primary_key=True, nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('enabled', sa.Boolean(), nullable=True),
            sa.Column('model', sa.String(), nullable=True),
            sa.Column('prompt_template', sa.Text(), nullable=True),
            sa.Column('params', sa.JSON(), nullable=True),
            sa.Column('weight', sa.Integer(), nullable=True),
            sa.Column('rules', sa.JSON(), nullable=True),
        )

    if not inspector.has_table('retrievermodel'):
        op.create_table(
            'retrievermodel',
            sa.Column('id', sa.String(), primary_key=True, nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('enabled', sa.Boolean(), nullable=True),
            sa.Column('connection', sa.JSON(), nullable=True),
            sa.Column('strategy', sa.JSON(), nullable=True),
            sa.Column('weight', sa.Integer(), nullable=True),
        )

    if not inspector.has_table('deliverychannelmodel'):
        op.create_table(
            'deliverychannelmodel',
            sa.Column('id', sa.String(), primary_key=True, nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('enabled', sa.Boolean(), nullable=True),
            sa.Column('config', sa.JSON(), nullable=True),
        )

    if not inspector.has_table('hitlrulemodel'):
        op.create_table(
            'hitlrulemodel',
            sa.Column('id', sa.String(), primary_key=True, nullable=False),
            sa.Column('enabled', sa.Boolean(), nullable=True),
            sa.Column('conditions', sa.JSON(), nullable=True),
            sa.Column('route_to', sa.String(), nullable=True),
            sa.Column('priority', sa.Integer(), nullable=True),
            sa.Column('sample_rate', sa.Integer(), nullable=True),
        )


def downgrade() -> None:
    """Drop the tables created in upgrade."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if inspector.has_table('hitlrulemodel'):
        op.drop_table('hitlrulemodel')
    if inspector.has_table('deliverychannelmodel'):
        op.drop_table('deliverychannelmodel')
    if inspector.has_table('retrievermodel'):
        op.drop_table('retrievermodel')
    if inspector.has_table('generatormodel'):
        op.drop_table('generatormodel')
