"""add reminders table

Revision ID: 002_add_reminders
Revises: 001_add_total_manager
Create Date: 2026-01-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_reminders'
down_revision: Union[str, None] = '001_add_total_manager'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tm_reminders table
    op.create_table(
        'tm_reminders',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('collection_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('repeat_type', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('is_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['collection_id'], ['tm_collections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tm_reminders_user_id', 'tm_reminders', ['user_id'], unique=False)
    op.create_index('ix_tm_reminders_scheduled_at', 'tm_reminders', ['scheduled_at'], unique=False)
    op.create_index('ix_tm_reminders_user_scheduled', 'tm_reminders', ['user_id', 'scheduled_at'], unique=False)
    op.create_index('ix_tm_reminders_user_sent', 'tm_reminders', ['user_id', 'is_sent'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_tm_reminders_user_sent', table_name='tm_reminders')
    op.drop_index('ix_tm_reminders_user_scheduled', table_name='tm_reminders')
    op.drop_index('ix_tm_reminders_scheduled_at', table_name='tm_reminders')
    op.drop_index('ix_tm_reminders_user_id', table_name='tm_reminders')
    op.drop_table('tm_reminders')

