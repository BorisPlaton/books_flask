from flask import Blueprint, url_for, redirect, flash, render_template, request
from flask_login import login_required, current_user

from bookreview import bookcover, db
from bookreview.forms import AddBook, WriteReview, WriteComment
from bookreview.models import Book, Review, User, Comment
from bookreview.utils import confirmed_required

book = Blueprint('book', __name__)


@book.route('/add_book', methods=["POST", "GET"])
@login_required
@confirmed_required
def add_book():
    """
    Добавление новой книги. Показывает уже добавленные книги.
    """
    add_book_form = AddBook()
    page = request.args.get('page', 1, type=int)
    books = current_user.books.paginate(per_page=9, page=page)
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
    book_ = Book.query.get_or_404(int(book_id))
    if current_user.id == book_.user.id:
        db.session.delete(book_)
        db.session.commit()
        next_route = request.args.get("next")
        flash("Книга удалена", category="warning")
        return redirect(url_for(next_route))
    return redirect(url_for('main.index'))


@book.route('/review/<int:review_id>', methods=["POST", "GET"])
@confirmed_required
def review(review_id):
    page = request.args.get('page', 1, type=int)
    current_review = Review.query.get_or_404(review_id)
    comments = current_review.comments.order_by(Comment.date.desc()).paginate(per_page=25, page=page)
    author_review = current_review.author.id

    write_comment = WriteComment()
    if write_comment.validate_on_submit():
        comment = Comment(author_id=current_user.id,
                          review_id=review_id,
                          text=write_comment.text.data)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('book.review', review_id=review_id, page=page))

    return render_template('review.html', review=current_review,
                           form=write_comment,
                           author_id=author_review,
                           comments=comments)


@book.route('/write_review', methods=["POST", "GET"])
@login_required
@confirmed_required
def write_review():
    write_review_form = WriteReview()
    if write_review_form.validate_on_submit():
        review_ = Review(author_id=current_user.id,
                         book_id=write_review_form.select_book.data.id,
                         text=write_review_form.text.data)
        db.session.add(review_)
        db.session.commit()
        flash("Запись сохранена", category="success")
        return redirect(url_for('main.profile', profile_id=current_user.id))

    return render_template("write_review.html", form=write_review_form)


@book.route('/delete_review/<int:review_id>')
@login_required
def delete_review(review_id):
    review_ = Review.query.get_or_404(int(review_id))
    if current_user.id == review_.author.id:
        db.session.delete(review_)
        db.session.commit()
        flash("Рецензия удалена", category="warning")
        return redirect(request.referrer)
    return redirect(url_for('main.index'))


@book.route('/delete_comment/<comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(int(comment_id))
    if current_user.id == comment.review.author.id:
        db.session.delete(comment)
        db.session.commit()
        return redirect(request.referrer)
    return redirect(url_for('main.index'))


@book.route('/status_up/<int:review_id>')
@login_required
def status_up(review_id):
    """
    Ставит лайк на пост
    :param review_id: ID Поста, на который ставят лайк
    """
    c_review = Review.query.get(review_id)

    # Делаем анализ. Если лайк уже стоял, то убираем его,
    # если нет, то наоборот ставим. Делаем изменения в
    # соответствующей таблице.
    if current_user in c_review.users_like:
        current_user.likes.remove(c_review)
        c_review.popularity -= 1
    else:
        current_user.likes.append(c_review)
        if c_review in current_user.dislikes:
            current_user.dislikes.remove(c_review)
        c_review.popularity += 1
    db.session.commit()
    return redirect(request.referrer)


@book.route('/status_down/<int:review_id>')
@login_required
def status_down(review_id):
    """
    Ставит дизлайк на пост
    :param review_id: ID Пост, на который ставят дизлайк
    """
    c_review = Review.query.get(review_id)

    # Делаем анализ. Если дизлайк уже стоял, то убираем его,
    # если нет, то наоборот ставим. Делаем изменения в
    # соответствующей таблице.
    if c_review in current_user.dislikes:
        current_user.dislikes.remove(c_review)
        c_review.popularity += 1
    else:
        current_user.dislikes.append(c_review)
        c_review.popularity -= 1
        if c_review in current_user.likes:
            current_user.likes.remove(c_review)
    db.session.commit()
    return redirect(request.referrer)
