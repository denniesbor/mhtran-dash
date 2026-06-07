"""add geomag scenario EAD columns (100yr and 250yr)

Revision ID: b3c1e9f72d88
Revises: 5a5f9d26aa40
Create Date: 2026-06-07
"""
from alembic import op
import sqlalchemy as sa

revision = "b3c1e9f72d88"
down_revision = "5a5f9d26aa40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("substations", sa.Column("ead_geomag_100", sa.Float(), nullable=True))
    op.add_column("substations", sa.Column("ead_geomag_250", sa.Float(), nullable=True))
    op.create_index("ix_substations_ead_geomag_100", "substations", ["ead_geomag_100"])
    op.create_index("ix_substations_ead_geomag_250", "substations", ["ead_geomag_250"])


def downgrade() -> None:
    op.drop_index("ix_substations_ead_geomag_250", table_name="substations")
    op.drop_index("ix_substations_ead_geomag_100", table_name="substations")
    op.drop_column("substations", "ead_geomag_250")
    op.drop_column("substations", "ead_geomag_100")
