from pathlib import Path
from os import remove
from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import generate_password_hash
from flask_uploads import UploadSet, IMAGES
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from bookreview.forms import LoadPhoto, DeletePhoto
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
def settings():
    load_photo = LoadPhoto()
    delete_photo = DeletePhoto()

    # Загрузка фотографии профиля
    if load_photo.validate_on_submit():
        if not current_user.profile_photo == "standard_user_pic.jpg":
            path = Path(Path.cwd(), "bookreview", "static", "profile_img", current_user.profile_photo)
            remove(path)
        current_user.profile_photo = profile_img.save(load_photo.photo.data)
        db.session.commit()
        return redirect(url_for('main.settings'))

    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo)


@main.route("/delete_photo", methods=["POST"])
def delete_user_img():
    delete_photo = DeletePhoto()
    # Удаление фото профиля
    if delete_photo.validate_on_submit():
        if not current_user.profile_photo == "standard_user_pic.jpg":
            path = Path(Path.cwd(), "bookreview", "static", "profile_img", current_user.profile_photo)
            remove(path)
            current_user.profile_photo = "standard_user_pic.jpg"
            db.session.commit()
        return redirect(url_for("main.settings"))
