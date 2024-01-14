"""Initial migration.

Revision ID: c12a5eb7cbda
Revises: 
Create Date: 2024-01-14 11:44:36.475447

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c12a5eb7cbda'
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
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('google_id', sa.String(length=120), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('given_name', sa.String(length=255), nullable=True),
    sa.Column('family_name', sa.String(length=255), nullable=True),
    sa.Column('picture', sa.String(length=255), nullable=True),
    sa.Column('locale', sa.String(length=10), nullable=True),
    sa.Column('account_type', sa.String(length=20), nullable=True),
    sa.Column('stripe_customer_id', sa.String(length=50), nullable=True),
    sa.Column('subscription_purchased', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('google_id'),
    sa.UniqueConstraint('stripe_customer_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('file_uploads')
    # ### end Alembic commands ###
