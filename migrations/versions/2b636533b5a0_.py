"""empty message

Revision ID: 2b636533b5a0
Revises: aa06513bb722
Create Date: 2020-05-27 14:08:16.573604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b636533b5a0'
down_revision = 'aa06513bb722'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('los', sa.Column('reputations', sa.Integer(), nullable=False))
    op.drop_column('los', 'reputation')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('los', sa.Column('reputation', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('los', 'reputations')
    # ### end Alembic commands ###
