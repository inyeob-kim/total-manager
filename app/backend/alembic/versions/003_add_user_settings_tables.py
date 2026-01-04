"""add user settings tables

Revision ID: 003_add_user_settings
Revises: 002_add_reminders
Create Date: 2026-01-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_add_user_settings'
down_revision: Union[str, None] = '002_add_reminders'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_settings table
    op.create_table(
        'user_settings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('push_notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reminder_notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'], unique=True)
    
    # Create user_payment_methods table
    op.create_table(
        'user_payment_methods',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('bank_name', sa.String(), nullable=False),
        sa.Column('account_number', sa.String(), nullable=False),
        sa.Column('account_holder', sa.String(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_payment_methods_user_id', 'user_payment_methods', ['user_id'], unique=False)
    op.create_index('ix_user_payment_methods_user_default', 'user_payment_methods', ['user_id', 'is_default'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_payment_methods_user_default', table_name='user_payment_methods')
    op.drop_index('ix_user_payment_methods_user_id', table_name='user_payment_methods')
    op.drop_table('user_payment_methods')
    op.drop_index('ix_user_settings_user_id', table_name='user_settings')
    op.drop_table('user_settings')

