from flask import url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from bookreview import mail, app


def send_reset_message(user, option):
    """
    Отправляет лист на почту со ссылкой для сброса пароля или логина, что указана в параметре email.

    :param user: Пользователь, которому отправляется письмо
    :param option: Что нужно изменить: логин или пароль
    """

    msg = Message(f'Восстановление {option}', recipients=[user.email])
    msg.body = f"""
                Ссылка для сброса {option}: {url_for('routes.confirm',
                                                     token=user.get_reset_token(),
                                                     option=option,
                                                     _external=True)}
                Если вы этого не делали, тогда просто проигнорируйте это письмо.
                """
    mail.send(msg)


def send_confirm_message(user_info: dict):
    """
    Отправляет письмо с подтверждением регистрации

    :param user_info: Информация о пользователе
    """

    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    token = s.dumps(user_info)
    msg = Message(f'Подтверждение регистрации', recipients=[user_info["email"]])
    msg.body = f"""Перейдите по ссылке, чтоб зарегистрироваться, если вы этого не делали, тогда просто проигнорируйте это письмо:
{url_for('routes.confirm_registration', token=token, _external=True)}"""
    mail.send(msg)
