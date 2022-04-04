from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def not_found(e):
    description_error = """
    Такого URL-адреса не существует, если вы вводили адрес вручную, проверьте его написание и попробуйте снова.
    """
    return render_template("error.html", e=e, description_error=description_error), 404


@errors.app_errorhandler(403)
def forbidden(e):
    description_error = """
    Вы не можете перейти по данному URL-адресу, так как у вас не хватает прав.
    """
    return render_template("error.html", e=e, description_error=description_error), 403
