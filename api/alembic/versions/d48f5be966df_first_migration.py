"""First migration

Revision ID: d48f5be966df
Revises: 
Create Date: 2021-06-06 16:10:44.779460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd48f5be966df'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('camera',
    sa.Column('eliminado', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('location_lat', sa.Float(), nullable=True),
    sa.Column('location_lng', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_camera_id'), 'camera', ['id'], unique=False)
    op.create_table('alert',
    sa.Column('eliminado', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('camera_id', sa.Integer(), nullable=True),
    sa.Column('details', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['camera_id'], ['camera.id'], name='Alert_Camera_FK'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_id'), 'alert', ['id'], unique=False)
    op.create_table('cameraevent',
    sa.Column('eliminado', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data', sa.String(), nullable=True),
    sa.Column('camera_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['camera_id'], ['camera.id'], name='CameraEvent_Camera_FK'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cameraevent_id'), 'cameraevent', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_cameraevent_id'), table_name='cameraevent')
    op.drop_table('cameraevent')
    op.drop_index(op.f('ix_alert_id'), table_name='alert')
    op.drop_table('alert')
    op.drop_index(op.f('ix_camera_id'), table_name='camera')
    op.drop_table('camera')
    # ### end Alembic commands ###