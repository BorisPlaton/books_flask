from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import generate_password_hash
from flask_uploads import UploadSet, IMAGES
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from bookreview.forms import LoadPhoto
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

    if load_photo.validate_on_submit():
        filename = profile_img.save(load_photo.photo.data)
        return f"{filename}"

    return render_template('settings.html', form=load_photo)
