"""add incident reference code

Revision ID: fdda7874e9ad
Revises: d112464ccd63
Create Date: 2026-09-17 13:37:49.898734
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdda7874e9ad'
down_revision: Union[str, None] = 'd112464ccd63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "incidents", sa.Column("reference", sa.String(length=16), nullable=False)
    )
    op.create_unique_constraint("uq_incidents_reference", "incidents", ["reference"])


def downgrade() -> None:
    op.drop_constraint("uq_incidents_reference", "incidents", type_="unique")
    op.drop_column("incidents", "reference")
