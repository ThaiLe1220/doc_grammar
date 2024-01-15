"""Initial migration.

Revision ID: ba361ef983dd
Revises: 
Create Date: 2024-01-15 14:41:29.063524

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ba361ef983dd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_uploads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=False),
    sa.Column('upload_time', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('corrections', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('file_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('file_uploads')
    # ### end Alembic commands ###