"""Add missing cols

Revision ID: 1f88475f3c3a
Revises: d48f5be966df
Create Date: 2021-06-06 16:23:09.915103

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f88475f3c3a'
down_revision = 'd48f5be966df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('camera', sa.Column('mock_resource', sa.String(), nullable=True))
    op.add_column('cameraevent', sa.Column('created_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cameraevent', 'created_date')
    op.drop_column('camera', 'mock_resource')
    # ### end Alembic commands ###
