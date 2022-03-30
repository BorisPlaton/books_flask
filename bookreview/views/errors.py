from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(Exception)
def not_found(e):
    return render_template("error.html", e=e), 404
