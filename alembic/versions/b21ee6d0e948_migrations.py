"""migrations

Revision ID: b21ee6d0e948
Revises: c354e4fddfa8
Create Date: 2025-01-15 13:56:51.192115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b21ee6d0e948'
down_revision: Union[str, None] = 'c354e4fddfa8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('bought_text_limits_count', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('bought_image_limits_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'bought_image_limits_count')
    op.drop_column('users', 'bought_text_limits_count')
    # ### end Alembic commands ###
