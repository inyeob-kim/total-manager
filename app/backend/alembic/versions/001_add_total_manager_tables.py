"""add total_manager tables

Revision ID: 001_add_total_manager
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_add_total_manager'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    op.execute("""
        CREATE TYPE grouptype AS ENUM ('parents', 'club', 'study', 'other');
    """)
    op.execute("""
        CREATE TYPE paymenttype AS ENUM ('bank', 'link');
    """)
    op.execute("""
        CREATE TYPE collectionstatus AS ENUM ('active', 'due_soon', 'closed');
    """)
    op.execute("""
        CREATE TYPE logtype AS ENUM ('notice_sent', 'read', 'paid_marked', 'reminder_scheduled', 'reminder_sent');
    """)
    
    # Create tm_groups table
    op.create_table(
        'tm_groups',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', postgresql.ENUM('parents', 'club', 'study', 'other', name='grouptype', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tm_groups_owner_id', 'tm_groups', ['owner_id'], unique=False)
    
    # Create tm_collections table
    op.create_table(
        'tm_collections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('group_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('payment_type', postgresql.ENUM('bank', 'link', name='paymenttype', create_type=False), nullable=False),
        sa.Column('payment_value', sa.String(), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'due_soon', 'closed', name='collectionstatus', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['tm_groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tm_collections_group_id', 'tm_collections', ['group_id'], unique=False)
    
    # Create tm_member_status table
    op.create_table(
        'tm_member_status',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('collection_id', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['tm_collections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tm_member_status_collection_id', 'tm_member_status', ['collection_id'], unique=False)
    
    # Create tm_event_logs table
    op.create_table(
        'tm_event_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('collection_id', sa.String(), nullable=False),
        sa.Column('type', postgresql.ENUM('notice_sent', 'read', 'paid_marked', 'reminder_scheduled', 'reminder_sent', name='logtype', create_type=False), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['tm_collections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tm_event_logs_collection_created', 'tm_event_logs', ['collection_id', sa.text('created_at DESC')], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index('ix_tm_event_logs_collection_created', table_name='tm_event_logs')
    op.drop_table('tm_event_logs')
    op.drop_index('ix_tm_member_status_collection_id', table_name='tm_member_status')
    op.drop_table('tm_member_status')
    op.drop_index('ix_tm_collections_group_id', table_name='tm_collections')
    op.drop_table('tm_collections')
    op.drop_index('ix_tm_groups_owner_id', table_name='tm_groups')
    op.drop_table('tm_groups')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS logtype;")
    op.execute("DROP TYPE IF EXISTS collectionstatus;")
    op.execute("DROP TYPE IF EXISTS paymenttype;")
    op.execute("DROP TYPE IF EXISTS grouptype;")

