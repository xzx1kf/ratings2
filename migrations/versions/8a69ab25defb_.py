"""empty message

Revision ID: 8a69ab25defb
Revises: a95795347d86
Create Date: 2017-03-08 14:08:56.610514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a69ab25defb'
down_revision = 'a95795347d86'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('league_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('league_id', sa.Integer(), nullable=True),
    sa.Column('avg_home_goals', sa.Float(), nullable=True),
    sa.Column('avg_away_goals', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['league_id'], ['league.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('league_stats')
    # ### end Alembic commands ###
