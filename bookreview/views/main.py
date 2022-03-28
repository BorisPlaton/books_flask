from flask import Blueprint, render_template
from flask_login import login_required, current_user
from bookreview.forms import LoadPhoto, DeletePhoto, ChangeUsername, WriteReview
from bookreview.models import Review, User

main = Blueprint("main", __name__)


@main.route('/')
def index():
    """
    Домашняя страница.
    """
    return render_template('index.html')


@main.route('/profile/<int:profile_id>', methods=["POST", "GET"])
@login_required
def profile(profile_id):
    user = User.query.get(profile_id)
    likes = 0
    dislikes = 0
    for review in user.reviews:
        likes += len(review.users_like)
        dislikes += len(review.users_dislike)
    return render_template("my_profile.html",
                           user=user,
                           likes=likes,
                           dislikes=dislikes)


@main.route('/settings')
@login_required
def settings():
    """
    Страница настроек. Обработчики форм вынесены в модуль bookreview.views.settings
    """
    load_photo = LoadPhoto()
    delete_photo = DeletePhoto()
    change_username = ChangeUsername()

    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo,
                           change_username_form=change_username)
