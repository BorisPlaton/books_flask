from flask import Blueprint, render_template, url_for, redirect
from bookreview.forms import LoginForm, RegisterForm

routes = Blueprint('routes', __name__)


@routes.route('/')
def index():
    """
    Домашняя страница.
    """
    return render_template('index.html')


@routes.route('/login', methods=["POST", "GET"])
def login():
    """
    Страница авторизации.
    """
    login_form = LoginForm()
    if login_form.validate_on_submit():
        return f"login {login_form.login.data} password {login_form.password.data} remember {login_form.remember.data}"
    return render_template('login.html', form=login_form)


@routes.route('/register', methods=["POST", "GET"])
def register():
    """
    Страница регистрации.
    """
    register_form = RegisterForm()
    return render_template('register.html', form=register_form)
