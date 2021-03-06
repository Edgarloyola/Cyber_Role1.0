"""empty message

Revision ID: 099959146ef3
Revises: bc067eac7008
Create Date: 2020-05-31 00:18:58.881191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '099959146ef3'
down_revision = 'bc067eac7008'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('fitness_cost', sa.Float(), nullable=False))
    op.add_column('courses', sa.Column('fitness_learning_goal', sa.Float(), nullable=False))
    op.add_column('courses', sa.Column('fitness_reputation', sa.Float(), nullable=False))
    op.add_column('courses', sa.Column('fitness_time', sa.Float(), nullable=False))
    op.drop_constraint('los_course_id_fkey', 'los', type_='foreignkey')
    op.drop_column('los', 'course_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('los', sa.Column('course_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('los_course_id_fkey', 'los', 'courses', ['course_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.drop_column('courses', 'fitness_time')
    op.drop_column('courses', 'fitness_reputation')
    op.drop_column('courses', 'fitness_learning_goal')
    op.drop_column('courses', 'fitness_cost')
    # ### end Alembic commands ###
