"""Add notification_metadata column

Revision ID: 6597e9c0973a
Revises: 8c56315e72df
Create Date: 2026-02-10 07:48:01.095511

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '6597e9c0973a'
down_revision = '8c56315e72df'
branch_labels = None
depends_on = None


def upgrade():
    # Add the missing column
    op.add_column('notifications',
        sa.Column('notification_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )


def downgrade():
    op.drop_column('notifications', 'notification_metadata')
