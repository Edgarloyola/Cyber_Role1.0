"""empty message

Revision ID: eda182a8f1c5
Revises: 4fe5429f8a2e
Create Date: 2020-06-12 14:25:01.583468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eda182a8f1c5'
down_revision = '4fe5429f8a2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('course_los')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course_los',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('course_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('lo_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name='course_los_course_id_fkey', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['lo_id'], ['los.id'], name='course_los_lo_id_fkey', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='course_los_pkey')
    )
    # ### end Alembic commands ###
