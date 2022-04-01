from flask import Blueprint, render_template, request
from flask_login import login_required

from bookreview.forms import LoadPhoto, DeletePhoto, ChangeUsername
from bookreview.models import Review, User

main = Blueprint("main", __name__)


@main.route('/')
def index():
    """
    Домашняя страница.
    """
    page = request.args.get("page", 1, type=int)
    reviews = Review.query.order_by(Review.date.desc(), Review.popularity.desc()).paginate(per_page=12,
                                                                                           page=page)
    return render_template('index.html', reviews=reviews)


@main.route('/profile/<int:profile_id>', methods=["POST", "GET"])
def profile(profile_id):
    page = request.args.get("page", 1, type=int)
    user = User.query.get_or_404(profile_id)
    user_reviews = user.reviews.order_by(Review.post_time.desc()).paginate(per_page=7, page=page)
    return render_template("my_profile.html", user=user, reviews=user_reviews)


@main.route('/settings')
@login_required
def settings():
    """
    Страница настроек. Обработчики форм вынесены в модуль bookreview.views.settings
    """
    load_photo = LoadPhoto()
    delete_photo = DeletePhoto()
    change_username = ChangeUsername()

    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo,
                           change_username_form=change_username)
