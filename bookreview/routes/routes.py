from flask import Blueprint, render_template, url_for, redirect


routes = Blueprint('main', __name__)


@routes.route('/')
def index():
    """
    Домашняя страница.
    """
    return render_template('index.html')


@routes.route('/login')
def login():
    """
    Страница авторизации.
    """
    return render_template('login.html')


@routes.route('/register')
def register():
    """
    Страница регистрации.
    """
    return render_template('register.html')
