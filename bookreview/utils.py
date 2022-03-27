from os import environ
from flask import url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from bookreview import mail


def send_reset_message(user):
    """
    Отправляет лист на почту пользователя со ссылкой для изменения пароля.

    :param user: Пользователь, которому отправляется письмо
    """
    s = URLSafeTimedSerializer(environ.get("SECRET_KEY"))
    token = s.dumps({"id": user.id})
    msg = Message(f'Изменение пароля', recipients=[user.email])
    msg.body = f"""Перейдите по ссылке, чтоб изменить пароль, если вы этого не делали, тогда просто проигнорируйте это письмо: 
{url_for('authorization.set_new_password', token=token, _external=True)}"""
    mail.send(msg)


def send_confirm_message(user_info: dict):
    """
    Отправляет письмо с подтверждением регистрации

    :param user_info: Информация о пользователе
    """
    s = URLSafeTimedSerializer(environ.get("SECRET_KEY"))
    token = s.dumps(user_info)
    msg = Message(f'Подтверждение регистрации', recipients=[user_info["email"]])
    msg.body = f"""Перейдите по ссылке, чтоб зарегистрироваться, если вы этого не делали, тогда просто проигнорируйте это письмо:
{url_for('authorization.confirm_registration', token=token, _external=True)}"""
    mail.send(msg)
