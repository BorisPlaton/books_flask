from flask import Blueprint, url_for, redirect, flash, render_template, request, abort
from flask_login import login_required, current_user

from bookreview import bookcover, db
from bookreview.forms import AddBook, WriteReview, WriteComment, SearchQuery
from bookreview.models import Book, Review, User, Comment, Permissions
from decorators import permission_required

book = Blueprint('book', __name__)


@book.route('/books/<int:user_id>', methods=["POST", "GET"])
@login_required
def add_book(user_id):
    """
    Добавление новой книги. Показывает уже добавленные книги.
    """
    add_book_form = AddBook()
    search_form = SearchQuery()
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    books = user.books.paginate(per_page=9, page=page)
    if add_book_form.validate_on_submit():
        if current_user.can(Permissions.WRITE):
            new_book = Book(user_id=current_user.id,
                            title=add_book_form.title.data,
                            author=add_book_form.author.data,
                            cover=bookcover.save(add_book_form.cover.data) if add_book_form.cover.data else None,
                            description=add_book_form.description.data)
            db.session.add(new_book)
            db.session.commit()
            flash("Книга добавлена", category="success")
        else:
            flash('Подтвердите аккаунт, чтоб добавлять книги', category='warning')
        return redirect(url_for('book.add_book', user_id=user_id))

    return render_template('add_book.html', form=add_book_form, books=books, user=user, search_form=search_form)


@book.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    book_ = Book.query.get_or_404(int(book_id))

    if current_user.id != book_.user.id and not current_user.can(Permissions.ADMINISTER):
        abort(403)

    db.session.delete(book_)
    db.session.commit()
    flash("Книга удалена", category="warning")
    return redirect(request.referrer)


@book.route('/review/<int:review_id>', methods=["POST", "GET"])
def review(review_id):
    page = request.args.get('page', 1, type=int)
    current_review = Review.query.get_or_404(review_id)
    comments = current_review.comments.order_by(Comment.date.desc()).paginate(per_page=25, page=page)
    author_review = current_review.author.id
    search_form = SearchQuery()
    write_comment = WriteComment()
    if write_comment.validate_on_submit():
        if current_user.can(Permissions.WRITE):
            comment = Comment(author_id=current_user.id,
                              review_id=review_id,
                              text=write_comment.text.data)
            db.session.add(comment)
            db.session.commit()
        elif current_user.is_anonymous:
            flash('Войдите в аккаунт', category='warning')
        elif not current_user.confirmed:
            flash('Подтвердите свой аккаунт', category='warning')
        else:
            flash('Вы не можете писать комментарии', category='warning')
        return redirect(url_for('book.review', review_id=review_id, page=page))

    return render_template('review.html', review=current_review,
                           form=write_comment,
                           author_id=author_review,
                           comments=comments,
                           search_form=search_form)


@book.route('/reviews/<int:user_id>', methods=["POST", "GET"])
@login_required
def write_review(user_id):
    search_form = SearchQuery()
    user = User.query.get(user_id)
    page = request.args.get('page', 1, type=int)
    reviews = user.reviews.order_by(Review.date.desc(), Review.popularity.desc()).paginate(per_page=15, page=page)
    write_review_form = WriteReview()
    if write_review_form.validate_on_submit() and current_user.can(Permissions.WRITE):
        review_ = Review(author_id=current_user.id,
                         book_id=write_review_form.select_book.data.id,
                         text=write_review_form.text.data)
        db.session.add(review_)
        db.session.commit()
        flash("Запись сохранена", category="success")
        return redirect(url_for('main.profile', profile_id=current_user.id))

    return render_template("write_review.html", form=write_review_form, user=user, page=page,
                           reviews=reviews, search_form=search_form)


@book.route('/delete_review/<int:review_id>')
@login_required
def delete_review(review_id):
    review_ = Review.query.get_or_404(int(review_id))
    if current_user.id != review_.author.id and not current_user.can(Permissions.ADMINISTER):
        abort(403)
    db.session.delete(review_)
    db.session.commit()
    flash("Рецензия удалена", category="warning")
    next_page = request.args.get('next')
    return redirect(next_page if next_page else request.referrer)


@book.route('/delete_comment/<comment_id>')
@login_required
@permission_required(Permissions.DELETE)
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(int(comment_id))
    if current_user.id != comment.author.id and not current_user.can(Permissions.MODERATE_COMS):
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    return redirect(request.referrer)


@book.route('/status_up/<int:review_id>')
@login_required
@permission_required(Permissions.WRITE)
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
        c_review.popularity += 1
        if c_review in current_user.dislikes:
            status_down(review_id)
    db.session.commit()
    return redirect(request.referrer)


@book.route('/status_down/<int:review_id>')
@login_required
@permission_required(Permissions.WRITE)
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
            status_up(review_id)
    db.session.commit()
    return redirect(request.referrer)
