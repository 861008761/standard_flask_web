"""add markdown

Revision ID: 4ca35bb162d6
Revises: 37bd248324c3
Create Date: 2015-12-05 20:11:20.246779

"""

# revision identifiers, used by Alembic.
revision = '4ca35bb162d6'
down_revision = '37bd248324c3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    ### end Alembic commands ###