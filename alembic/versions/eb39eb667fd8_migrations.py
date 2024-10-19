"""migrations

Revision ID: eb39eb667fd8
Revises: 
Create Date: 2024-10-19 17:20:31.356614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb39eb667fd8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('price_3', sa.Integer(), nullable=True),
    sa.Column('price_6', sa.Integer(), nullable=True),
    sa.Column('price_12', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('model_limits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rate_id', sa.Integer(), nullable=False),
    sa.Column('model', sa.String(), nullable=True),
    sa.Column('daily_limit', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rate_id'], ['rate.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_limits_rate_id'), 'model_limits', ['rate_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=False),
    sa.Column('chat_model', sa.Enum('GPT_4O', 'GPT_4O_MINI', name='chatmodelenum'), nullable=True),
    sa.Column('image_model', sa.Enum('DALL_E_3', name='imagemodelenum'), nullable=True),
    sa.Column('rate_id', sa.Integer(), nullable=False),
    sa.Column('last_activity_time', sa.DateTime(), nullable=True),
    sa.Column('registration_time', sa.DateTime(), nullable=True),
    sa.Column('subscription_end_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['rate_id'], ['rate.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_rate_id'), 'users', ['rate_id'], unique=False)
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)
    op.create_table('counts_of_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('model', sa.Enum('GPT_4O', 'GPT_4O_MINI', 'DALL_E_3', name='modelsenum'), nullable=True),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_counts_of_requests_user_id'), 'counts_of_requests', ['user_id'], unique=False)
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_user_id'), 'messages', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_counts_of_requests_user_id'), table_name='counts_of_requests')
    op.drop_table('counts_of_requests')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_rate_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_model_limits_rate_id'), table_name='model_limits')
    op.drop_table('model_limits')
    op.drop_table('rate')
    # ### end Alembic commands ###