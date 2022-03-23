from pathlib import Path
from os import remove
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import generate_password_hash
from flask_uploads import UploadSet, IMAGES
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from bookreview.forms import LoadPhoto, DeletePhoto, ChangeUsername, ChangePassword
from bookreview.models import User
from bookreview.func import send_reset_message, send_confirm_message
from bookreview import db, app, profile_img

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


@main.route("/load_photo", methods=["GET", "POST"])
@login_required
def load_photo_def():
    """
    Загружает фото пользователя
    """
    if request.method == "GET":
        return redirect(url_for("main.settings"))

    load_photo = LoadPhoto()
    delete_photo = DeletePhoto()
    change_username = ChangeUsername()
    if load_photo.validate_on_submit():
        if not current_user.profile_photo == "standard_user_pic.jpg":
            path = Path(Path.cwd(), "bookreview", "static", "profile_img", current_user.profile_photo)
            remove(path)
        current_user.profile_photo = profile_img.save(load_photo.photo.data)
        db.session.commit()
        return redirect(url_for("main.settings"))
    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo,
                           change_username_form=change_username)


@main.route("/change_username", methods=["GET", "POST"])
@login_required
def change_username_def():
    """
    Меняет имя пользователя
    """

    if request.method == "GET":
        return redirect(url_for("main.settings"))

    load_photo = LoadPhoto()
    delete_photo = DeletePhoto()
    change_username = ChangeUsername()
    if change_username.validate_on_submit():
        current_user.username = change_username.username.data
        db.session.commit()
        return redirect(url_for("main.settings"))
    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo,
                           change_username_form=change_username)


@main.route("/delete_photo", methods=["GET", "POST"])
@login_required
def delete_photo_def():
    """
    Удаляет фото пользователя, если это не стандартное фото
    """

    if request.method == "GET":
        return redirect(url_for("main.settings"))

    load_photo = LoadPhoto()
    delete_photo = DeletePhoto()
    change_username = ChangeUsername()
    if delete_photo.validate_on_submit():
        if not current_user.profile_photo == "standard_user_pic.jpg":
            path = Path(Path.cwd(), "bookreview", "static", "profile_img", current_user.profile_photo)
            remove(path)
            current_user.profile_photo = "standard_user_pic.jpg"
            db.session.commit()
            return redirect(url_for("main.settings"))
    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo,
                           change_username_form=change_username)


@main.route("/change_password", methods=["POST", "GET"])
@login_required
def change_password():
    change_password_form = ChangePassword()
    if change_password_form.validate_on_submit():
        current_user.password = generate_password_hash(change_password_form.new_password.data)
        db.session.commit()
        flash("Пароль успешно изменён", category="success")
        return redirect(url_for("main.settings"))
    return render_template("change_password.html", form=change_password_form)
