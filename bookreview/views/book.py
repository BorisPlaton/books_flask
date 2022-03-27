from flask import Blueprint, url_for, redirect, flash, render_template
from flask_login import login_required, current_user

from bookreview import bookcover, db
from bookreview.forms import AddBook, WriteReview
from bookreview.models import Book, Review

book = Blueprint('book', __name__)


@book.route('/add_book', methods=["POST", "GET"])
@login_required
def add_book():
    """
    Добавление новой книги. Показывает уже добавленные книги.
    """
    add_book_form = AddBook()
    books = current_user.books
    if add_book_form.validate_on_submit():
        new_book = Book(user_id=current_user.id,
                        title=add_book_form.title.data,
                        author=add_book_form.author.data,
                        cover=bookcover.save(add_book_form.cover.data) if add_book_form.cover.data else None,
                        description=add_book_form.description.data)
        db.session.add(new_book)
        db.session.commit()
        flash("Книга добавлена", category="success")
        return redirect(url_for('book.add_book'))

    return render_template('add_book.html', form=add_book_form, books=books)


@book.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    Book.query.filter_by(id=book_id).delete()
    db.session.commit()
    return redirect(url_for('book.add_book'))


@book.route('/write_review', methods=["POST", "GET"])
@login_required
def write_review():
    write_review_form = WriteReview()

    if write_review_form.validate_on_submit():
        review = Review()

    return render_template("write_review.html", form=write_review_form)
