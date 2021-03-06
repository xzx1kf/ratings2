"""empty message

Revision ID: 995116c4b8dd
Revises: 8a69ab25defb
Create Date: 2017-03-08 14:53:05.477701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '995116c4b8dd'
down_revision = '8a69ab25defb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('team_stats', sa.Column('attack_strength', sa.Float(), nullable=True))
    op.add_column('team_stats', sa.Column('defense_strength', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('team_stats', 'defense_strength')
    op.drop_column('team_stats', 'attack_strength')
    # ### end Alembic commands ###
