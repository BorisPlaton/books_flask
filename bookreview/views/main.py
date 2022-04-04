from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required

from bookreview.forms import LoadPhoto, Delete, ChangeUsername, SearchQuery
from bookreview.models import Review, User, Book

main = Blueprint("main", __name__)


@main.route('/', methods=["GET"])
def index():
    """
    Домашняя страница.
    """
    search_form = SearchQuery()
    page = request.args.get("page", 1, type=int)
    review_title = request.args.get('review_title')

    if review_title:
        reviews = Review.query.join(Book, Review.book_id == Book.id).filter(
            Book.title.like(f"%{review_title}%")).order_by(Review.date.desc(), Review.popularity.desc()).paginate(
            per_page=12, page=page)
    else:
        reviews = Review.query.order_by(Review.date.desc(), Review.popularity.desc()).paginate(per_page=12, page=page)

    return render_template('index.html', reviews=reviews, search_form=search_form, review_title=review_title)


@main.route('/search_bar', methods=["POST"])
def search_bar():
    search_form = SearchQuery()
    if search_form.validate_on_submit():
        if search_form.text.data and search_form.text.data[0] == "@":
            return redirect(url_for('main.users_list', username=search_form.text.data[1:]))
        return redirect(url_for('main.index', review_title=search_form.text.data))


@main.route('/profile/<int:profile_id>', methods=["POST", "GET"])
def profile(profile_id):
    search_form = SearchQuery()
    page = request.args.get("page", 1, type=int)
    user = User.query.get_or_404(profile_id)
    user_reviews = user.reviews.order_by(Review.post_time.desc()).paginate(per_page=7, page=page)
    return render_template("my_profile.html", user=user, reviews=user_reviews, search_form=search_form)


@main.route('/settings')
@login_required
def settings():
    """
    Страница настроек. Обработчики форм вынесены в модуль bookreview.views.settings
    """
    search_form = SearchQuery()
    load_photo = LoadPhoto()
    delete_photo = Delete()
    change_username = ChangeUsername()

    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo,
                           change_username_form=change_username,
                           search_form=search_form)


@main.route('/users')
def users_list():
    search_form = SearchQuery()
    page = request.args.get("page", 1, type=int)
    username = request.args.get('username')

    if username:
        users = User.query.filter(User.login.like(f"%{username}%")).paginate(per_page=25, page=page)
    else:
        users = User.query.paginate(per_page=25, page=page)

    return render_template("list_users.html", users=users, search_form=search_form)
