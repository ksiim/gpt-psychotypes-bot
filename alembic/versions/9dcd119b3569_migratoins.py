"""migratoins

Revision ID: 9dcd119b3569
Revises: b21b488fc707
Create Date: 2025-01-15 23:15:08.423134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dcd119b3569'
down_revision: Union[str, None] = 'b21b488fc707'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('psychotypes', sa.Column('statistics', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('psychotypes', 'statistics')
    # ### end Alembic commands ###
