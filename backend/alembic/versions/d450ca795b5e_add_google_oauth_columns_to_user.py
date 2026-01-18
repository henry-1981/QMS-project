"""add_google_oauth_columns_to_user

Revision ID: d450ca795b5e
Revises: ce4a8051b8d0
Create Date: 2026-01-16 20:04:32.395780

"""
from alembic import op
import sqlalchemy as sa


revision = 'd450ca795b5e'
down_revision = 'ce4a8051b8d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('google_refresh_token', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('google_access_token', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('google_token_expiry', sa.DateTime(timezone=True), nullable=True))
    
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)
    
    op.alter_column('users', 'password_hash', existing_type=sa.String(255), nullable=True)


def downgrade() -> None:
    op.alter_column('users', 'password_hash', existing_type=sa.String(255), nullable=False)
    
    op.drop_index('ix_users_google_id', table_name='users')
    
    op.drop_column('users', 'google_token_expiry')
    op.drop_column('users', 'google_access_token')
    op.drop_column('users', 'google_refresh_token')
    op.drop_column('users', 'google_id')
