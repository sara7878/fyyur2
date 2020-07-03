"""empty message

Revision ID: 49cec823add0
Revises: 051ca964b04d
Create Date: 2020-07-02 06:15:42.526904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49cec823add0'
down_revision = '051ca964b04d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('venues', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venues', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('artists', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###
