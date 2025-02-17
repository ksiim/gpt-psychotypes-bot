"""migratoins

Revision ID: b21b488fc707
Revises: 65db0784a6dc
Create Date: 2025-01-15 22:27:29.558797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b21b488fc707'
down_revision: Union[str, None] = '65db0784a6dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('purchases', 'payment_url')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('purchases', sa.Column('payment_url', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
