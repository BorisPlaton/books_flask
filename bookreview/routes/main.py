from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required
from flask_bcrypt import generate_password_hash
from bookreview.forms import LoadPhoto, DeletePhoto, ChangeUsername, ChangePassword
from bookreview import db, profile_img

main = Blueprint("main", __name__)


@main.route('/')
def index():
    """
    Домашняя страница.
    """
    return render_template('index.html')


@main.route('/settings', methods=["POST", "GET"])
@login_required
def settings():
    """
    Страница настроек. Обработчики форм вынесены в отдельные функции:
    :func: load_photo_def - Загружает фото пользователя
    :func: change_username_def - Меняет имя пользователя
    :func: delete_photo_def - Удаляет фото пользователя
    """
    load_photo = LoadPhoto()
    delete_photo = DeletePhoto()
    change_username = ChangeUsername()

    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo,
                           change_username_form=change_username)


@main.route('/my_profile', methods=["POST", "GET"])
@login_required
def my_profile():
    return render_template("my_profile.html")
