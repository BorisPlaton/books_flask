from flask import Blueprint, url_for, redirect, flash, render_template, request
from flask_login import login_required, current_user

from bookreview import bookcover, db
from bookreview.forms import AddBook, WriteReview
from bookreview.models import Book, Review, User

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
    next_route = request.args.get("next")
    Book.query.filter_by(id=book_id).delete()
    db.session.commit()
    return redirect(url_for(next_route))


@book.route('/review/<int:review_id>')
def review(review_id):
    current_review = Review.query.get(review_id)
    return render_template('review.html', review=current_review)


@book.route('/write_review', methods=["POST", "GET"])
@login_required
def write_review():
    write_review_form = WriteReview()

    if write_review_form.validate_on_submit():
        review = Review(author_id=current_user.id,
                        book_id=write_review_form.select_book.data.id,
                        text=write_review_form.text.data)
        db.session.add(review)
        db.session.commit()
        flash("Рецензия сохранена", category="success")
        return redirect(url_for('main.my_profile'))

    return render_template("write_review.html", form=write_review_form)


@book.route('/delete_review/<int:review_id>')
@login_required
def delete_review(review_id):
    next_route = request.args.get("next")
    Review.query.filter_by(id=review_id).delete()
    db.session.commit()
    return redirect(url_for(next_route))


@book.route('/status_up/<int:user_id>/<int:review_id>')
@login_required
def status_up(user_id, review_id):
    """
    Ставит лайк на пост
    :param user_id: ID Пользователя, что ставит
    :param review_id: ID Поста, на который ставят
    """
    user = User.query.get(user_id)
    review = Review.query.get(review_id)
    next_page = request.args.get('next')

    # Делаем анализ. Если лайк уже стоял, то убираем его,
    # если нет, то наоборот ставим. Делаем изменения в
    # соответствующей таблице.
    if review in user.likes:
        user.likes.remove(review)
    else:
        user.likes.append(review)
        if review in user.dislikes:
            user.dislikes.remove(review)
    db.session.commit()
    return redirect(next_page)


@book.route('/status_down/<int:user_id>/<int:review_id>')
@login_required
def status_down(user_id, review_id):
    """
    Ставит дизлайк на пост
    :param user_id: ID Пользователя, что ставит
    :param review_id: ID Поста, на который ставят
    """
    user = User.query.get(user_id)
    review = Review.query.get(review_id)
    next_page = request.args.get('next')

    # Делаем анализ. Если дизлайк уже стоял, то убираем его,
    # если нет, то наоборот ставим. Делаем изменения в
    # соответствующей таблице.
    if review in user.dislikes:
        user.dislikes.remove(review)
    else:
        user.dislikes.append(review)
        if review in user.likes:
            user.likes.remove(review)
    db.session.commit()
    return redirect(next_page)
