from pathlib import Path
from os import remove
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

from bookreview import db, profile
from bookreview.forms import LoadPhoto, Delete, ChangeUsername, ChangePassword, DeleteAccount

settings = Blueprint("settings", __name__)


@settings.route("/load_photo", methods=["POST"])
@login_required
def load_photo_def():
    """
    Загружает фото пользователя
    """
    load_photo = LoadPhoto()
    if load_photo.validate_on_submit():
        if not current_user.profile_photo == "default_user_img.jpg":
            try:
                path = Path(Path.cwd(), "bookreview", "static", "profile_img", current_user.profile_photo)
                remove(path)
            except FileNotFoundError:
                pass
        current_user.profile_photo = profile.save(load_photo.photo.data)
        db.session.commit()
    else:
        for _, errors in load_photo.errors.items():
            for error in errors:
                flash(error, category='warning')
    return redirect(url_for("main.settings"))


@settings.route("/change_username", methods=["POST"])
@login_required
def change_username_def():
    """
    Меняет имя пользователя
    """
    change_username = ChangeUsername()
    if change_username.validate_on_submit():
        current_user.username = change_username.username.data
        db.session.commit()
    else:
        for _, errors in change_username.errors.items():
            for error in errors:
                flash(error, category='warning')
    return redirect(url_for("main.settings"))


@settings.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    delete_account_form = DeleteAccount()
    if delete_account_form.validate_on_submit():
        db.session.delete(current_user)
        db.session.commit()
        flash('Вы удалили свой аккаунт', category='success')
        return redirect(url_for('authorization.login'))
    return render_template('delete_account.html', form=delete_account_form)


@settings.route("/delete_photo", methods=["POST"])
@login_required
def delete_photo_def():
    """
    Удаляет фото пользователя, если это не стандартное фото
    """
    delete_photo = Delete()
    if delete_photo.validate_on_submit() and current_user.profile_photo != "default_user_img.jpg":
        path = Path(Path.cwd(), "bookreview", "static", "profile_img", current_user.profile_photo)
        remove(path)
        # Устанавливаем стандартное фото пользователя
        current_user.profile_photo = "default_user_img.jpg"
        db.session.commit()
    else:
        for _, errors in delete_photo.errors.items():
            for error in errors:
                flash(error, category='warning')
    return redirect(url_for("main.settings"))


@settings.route("/change_password", methods=["POST", "GET"])
@login_required
def change_password():
    """
    Меняет пароль пользователя. В отличие от bookreview.views.authorization.resset_password
    требует ввода старого пароля.
    """
    change_password_form = ChangePassword()
    if change_password_form.validate_on_submit():
        current_user.password = change_password_form.new_password.data
        db.session.commit()
        flash("Пароль успешно изменён", category="success")
        return redirect(url_for("main.settings"))
    return render_template("change_password.html", form=change_password_form)
