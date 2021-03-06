"""empty message

Revision ID: 73f9d45f9077
Revises: 2b636533b5a0
Create Date: 2020-05-27 14:10:13.555267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73f9d45f9077'
down_revision = '2b636533b5a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('los', sa.Column('reputation', sa.Integer(), nullable=False))
    op.drop_column('los', 'reputations')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('los', sa.Column('reputations', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('los', 'reputation')
    # ### end Alembic commands ###
