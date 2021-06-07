"""Add created date

Revision ID: 2654520e8836
Revises: 411441e7dd6f
Create Date: 2021-06-06 17:25:23.717299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2654520e8836'
down_revision = '411441e7dd6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alert', sa.Column('created_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('alert', 'created_date')
    # ### end Alembic commands ###
