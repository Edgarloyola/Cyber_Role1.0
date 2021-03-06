"""empty message

Revision ID: b20fafdb469c
Revises: 7f948701e409
Create Date: 2020-07-02 20:11:51.234752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b20fafdb469c'
down_revision = '7f948701e409'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('courses_user_id_fkey', 'courses', type_='foreignkey')
    op.drop_column('courses', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('courses_user_id_fkey', 'courses', 'users', ['user_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###
