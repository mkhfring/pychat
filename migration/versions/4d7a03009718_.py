"""empty message

Revision ID: 4d7a03009718
Revises: f49d94bb5933
Create Date: 2019-04-13 19:45:54.185405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d7a03009718'
down_revision = 'f49d94bb5933'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('envelop', sa.Column('origin_target_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('envelop', 'origin_target_id')
    # ### end Alembic commands ###