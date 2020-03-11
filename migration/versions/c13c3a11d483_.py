"""empty message

Revision ID: 2017c4ed3390
Revises: 3ad908e438de
Create Date: 2019-02-25 12:26:45.728875

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2017c4ed3390'
down_revision = '3ad908e438de'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE member_message RENAME TO member_message_seen;')
    op.execute(
        'ALTER INDEX member_message_pkey RENAME TO member_message_seen_pkey;'
    )
    op.execute(
        'ALTER TABLE member_message_seen RENAME CONSTRAINT '
        'member_message_member_id_fkey TO member_message_seen_member_id_fkey;'
    )
    op.execute(
        'ALTER TABLE member_message_seen RENAME CONSTRAINT '
        'member_message_message_id_fkey TO member_message_seen_message_id_fkey;'
    )
    # ### end Alembic commands ###


def downgrade():
    op.execute('ALTER TABLE member_message_seen RENAME TO member_message;')
    op.execute(
        'ALTER INDEX member_message_seen_pkey RENAME TO member_message_pkey;'
    )
    op.execute(
        'ALTER TABLE member_message RENAME CONSTRAINT '
        'member_message_seen_member_id_fkey TO member_message_member_id_fkey;'
    )
    op.execute(
        'ALTER TABLE member_message RENAME CONSTRAINT '
        'member_message_seen_message_id_fkey TO member_message_message_id_fkey;'
    )
    # ### end Alembic commands ###

