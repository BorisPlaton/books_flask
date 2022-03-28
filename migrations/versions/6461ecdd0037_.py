"""empty message

Revision ID: 6461ecdd0037
Revises: e782e3cc8d8f
Create Date: 2022-03-28 00:50:49.637298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6461ecdd0037'
down_revision = 'e782e3cc8d8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('review_ibfk_1', 'review', type_='foreignkey')
    op.create_foreign_key(None, 'review', 'user', ['author_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'review', type_='foreignkey')
    op.create_foreign_key('review_ibfk_1', 'review', 'user', ['author_id'], ['id'])
    # ### end Alembic commands ###