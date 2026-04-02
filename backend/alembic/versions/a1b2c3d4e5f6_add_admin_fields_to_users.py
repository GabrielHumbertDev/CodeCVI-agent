"""add admin fields to users

Revision ID: a1b2c3d4e5f6
Revises: f1d4fab49a79
Create Date: 2026-04-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'a1b2c3d4e5f6'
down_revision = 'f1d4fab49a79'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new admin/lifecycle columns to users table
    op.add_column('users', sa.Column('role', sa.String(20), nullable=False, server_default='user'))
    op.add_column('users', sa.Column('status', sa.String(30), nullable=False, server_default='active'))
    op.add_column('users', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('approved_by', UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('paused_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('pause_reason', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))

    # Existing users default to active (they were already working before admin system)
    op.execute("UPDATE users SET status = 'active', role = 'user' WHERE status IS NULL OR status = ''")


def downgrade() -> None:
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'pause_reason')
    op.drop_column('users', 'paused_at')
    op.drop_column('users', 'approved_by')
    op.drop_column('users', 'approved_at')
    op.drop_column('users', 'status')
    op.drop_column('users', 'role')
