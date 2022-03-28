"""empty message

Revision ID: 9a6bf9349448
Revises: 6461ecdd0037
Create Date: 2022-03-28 00:54:36.716211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a6bf9349448'
down_revision = '6461ecdd0037'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('book_ibfk_1', 'book', type_='foreignkey')
    op.create_foreign_key(None, 'book', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('comment_ibfk_2', 'comment', type_='foreignkey')
    op.drop_constraint('comment_ibfk_1', 'comment', type_='foreignkey')
    op.create_foreign_key(None, 'comment', 'review', ['review_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'comment', 'user', ['author_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('user_dislikes_ibfk_2', 'user_dislikes', type_='foreignkey')
    op.drop_constraint('user_dislikes_ibfk_1', 'user_dislikes', type_='foreignkey')
    op.create_foreign_key(None, 'user_dislikes', 'review', ['review_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'user_dislikes', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('user_likes_ibfk_2', 'user_likes', type_='foreignkey')
    op.drop_constraint('user_likes_ibfk_1', 'user_likes', type_='foreignkey')
    op.create_foreign_key(None, 'user_likes', 'review', ['review_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'user_likes', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_likes', type_='foreignkey')
    op.drop_constraint(None, 'user_likes', type_='foreignkey')
    op.create_foreign_key('user_likes_ibfk_1', 'user_likes', 'review', ['review_id'], ['id'])
    op.create_foreign_key('user_likes_ibfk_2', 'user_likes', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'user_dislikes', type_='foreignkey')
    op.drop_constraint(None, 'user_dislikes', type_='foreignkey')
    op.create_foreign_key('user_dislikes_ibfk_1', 'user_dislikes', 'review', ['review_id'], ['id'])
    op.create_foreign_key('user_dislikes_ibfk_2', 'user_dislikes', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.create_foreign_key('comment_ibfk_1', 'comment', 'user', ['author_id'], ['id'])
    op.create_foreign_key('comment_ibfk_2', 'comment', 'review', ['review_id'], ['id'])
    op.drop_constraint(None, 'book', type_='foreignkey')
    op.create_foreign_key('book_ibfk_1', 'book', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###