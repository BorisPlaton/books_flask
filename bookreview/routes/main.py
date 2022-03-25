from flask import Blueprint, render_template, flash, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from bookreview.forms import LoadPhoto, DeletePhoto, ChangeUsername, WriteReview, AddBook
from bookreview.models import Book
from bookreview import db

main = Blueprint("main", __name__)


@main.route('/')
def index():
    """
    Домашняя страница.
    """
    return render_template('index.html')


@main.route('/my_profile', methods=["POST", "GET"])
@login_required
def my_profile():
    return render_template("my_profile.html")


@main.route('/write_review', methods=["POST", "GET"])
@login_required
def write_review():
    write_review_form = WriteReview()

    return render_template("write_review.html", form=write_review_form)


@main.route('/add_book', methods=["POST", "GET"])
@login_required
def add_book():
    """
    Добавление новой книги. Показывает уже добавленные книги.
    """
    add_book_form = AddBook()

    if add_book_form.validate_on_submit():
        book = Book(title=add_book_form.title.data,
                    author=add_book_form.author.data,
                    cover=add_book_form.cover.data,
                    desription=add_book_form.description.data)
        db.session.add(book)
        db.session.commit()
        flash("Книга успешно добавлена!", category="success")
        return redirect(url_for('main.add_book'))

    return render_template('add_book.html', form=add_book_form)


@main.route('/settings')
@login_required
def settings():
    """
    Страница настроек. Обработчики форм вынесены в модуль bookreview.routes.settings
    """
    load_photo = LoadPhoto()
    delete_photo = DeletePhoto()
    change_username = ChangeUsername()

    return render_template('settings.html',
                           load_photo_form=load_photo,
                           delete_photo_form=delete_photo,
                           change_username_form=change_username)
