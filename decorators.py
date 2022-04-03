from functools import wraps

from flask import request, flash
from flask_login import current_user
from werkzeug.utils import redirect


def permission_required(permission):
    def decorated_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                flash('Вы не можете этого сделать', category='warning')
                return redirect(request.referrer)
            return func(*args, **kwargs)

        return wrapper

    return decorated_func
