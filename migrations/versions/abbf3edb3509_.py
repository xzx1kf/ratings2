"""empty message

Revision ID: abbf3edb3509
Revises: cf07dafc6f26
Create Date: 2017-03-17 14:02:01.716382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abbf3edb3509'
down_revision = 'cf07dafc6f26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('odds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fixture_id', sa.Integer(), nullable=True),
    sa.Column('home', sa.Float(), nullable=True),
    sa.Column('draw', sa.Float(), nullable=True),
    sa.Column('away', sa.Float(), nullable=True),
    sa.Column('over', sa.Float(), nullable=True),
    sa.Column('under', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['fixture_id'], ['fixture.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('fixture_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('odds')
    # ### end Alembic commands ###
