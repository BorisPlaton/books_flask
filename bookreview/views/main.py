from flask import Blueprint, render_template
from flask_login import login_required, current_user
from bookreview.forms import LoadPhoto, DeletePhoto, ChangeUsername, WriteReview
from bookreview.models import Review

main = Blueprint("main", __name__)


@main.route('/')
def index():
    """
    Домашняя страница.
    """
    return render_template('index.html')


@main.route('/my_profile', methods=["POST", "GET"])
@login_required
def my_profile():
    reviews = Review.query.filter_by(author_id=current_user.id).order_by(Review.date.desc()).all()
    likes = len(current_user.likes)
    dislikes = len(current_user.dislikes)
    return render_template("my_profile.html",
                           reviews=reviews,
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
