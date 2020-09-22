"""empty message

Revision ID: cf6908987d30
Revises: 2946c3056ec5
Create Date: 2020-09-22 14:20:07.688796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf6908987d30'
down_revision = '2946c3056ec5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    # ### end Alembic commands ###
