"""add users table

Revision ID: 004_add_users
Revises: 003_add_user_settings
Create Date: 2026-01-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004_add_users'
down_revision: Union[str, None] = '003_add_user_settings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('kakao_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('profile_image_url', sa.String(), nullable=True),
        sa.Column('is_onboarded', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_users_phone', 'users', ['phone'], unique=True)
    op.create_index('ix_users_kakao_id', 'users', ['kakao_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_kakao_id', table_name='users')
    op.drop_index('ix_users_phone', table_name='users')
    op.drop_table('users')

