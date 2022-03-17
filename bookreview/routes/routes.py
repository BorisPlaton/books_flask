from flask import Blueprint

routes = Blueprint('main', __name__)


@routes.route('/')
def index():
    return 'main page'


@routes.route('/login')
def login():
    return 'login page'


@routes.route('/register')
def register():
    return 'register page'
