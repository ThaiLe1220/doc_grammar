"""Added daily upload count to User model

Revision ID: 20c9651312e6
Revises: ba361ef983dd
Create Date: 2024-01-15 15:00:12.505429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20c9651312e6'
down_revision = 'ba361ef983dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('daily_upload_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_upload_date', sa.Date(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_upload_date')
        batch_op.drop_column('daily_upload_count')

    # ### end Alembic commands ###
