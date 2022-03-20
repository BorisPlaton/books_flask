from flask import Blueprint, render_template, url_for, redirect, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from bookreview.forms.forms import LoginForm, RegisterForm, EmailSendForm, SetNewPassword
from bookreview.models.models import User
from bookreview.func import send_reset_message, send_confirm_message
from bookreview import db, app

main = Blueprint("main", __name__)


@main.route('/')
def index():
    """
    Домашняя страница.
    """
    return render_template('index.html')
