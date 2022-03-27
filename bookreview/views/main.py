from flask import Blueprint, render_template
from flask_login import login_required, current_user
from bookreview.forms import LoadPhoto, DeletePhoto, ChangeUsername, WriteReview


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
    books = current_user.books
    return render_template("my_profile.html", books=False)


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