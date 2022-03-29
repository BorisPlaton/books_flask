import re

from flask import url_for
from flask_mail import Message

from bookreview import mail


def send_reset_message(user):
    """
    Отправляет лист на почту пользователя со ссылкой для изменения пароля.

    :param user: Пользователь, которому отправляется письмо
    """
    msg = Message(f'Изменение пароля', recipients=[user.email])
    msg.body = f"""Перейдите по ссылке, чтоб изменить пароль, если вы этого не делали, тогда просто проигнорируйте это письмо:
{url_for('authorization.set_new_password', token=user.generate_token(), _external=True)}"""
    mail.send(msg)


def send_confirm_message(user):
    """
    Отправляет письмо с подтверждением регистрации

    :param user: Пользователь
    """
    msg = Message(f'Подтверждение регистрации', recipients=[user.email])
    msg.body = f"""Перейдите по ссылке, чтоб зарегистрироваться, если вы этого не делали, тогда просто проигнорируйте это письмо:
{url_for('authorization.confirm_registration', token=user.generate_token(), user_id=user.id, _external=True)}"""
    mail.send(msg)


def month_translate(data: str, lang='rus') -> str:
    """
    Переводит название месяца с английского на язык, что указан в параметре lang.

    :param data: Строка с месяцем
    :param lang: Язык на который надо перевести
    :return: Строка с новым названием месяца
    """
    month = re.search("[a-zA-Z]+", data)
    month_table = {
        "rus": {
            "january": "января",
            "february": "февраля",
            "march": "марта",
            "april": "апреля",
            "may": "мая",
            "june": "июня",
            "july": "июля",
            "august": "августа",
            "september": "сентября",
            "october": "октября",
            "november": "ноября",
            "december": "декабря"
        }
    }
    if month:
        assert month.group().lower() in month_table[lang]
        return data.replace(month.group(), month_table[lang][month.group().lower()].capitalize())


# def delete_gaps(text: str) -> str:
#     """
#     Удаляет лишние теги <br> в тексте
#
#     :param text: Текст, что нужно отредактировать
#     :return: Текст без лишних тегов <br>
#     """
#     pattern = "(?:\\r\\n\\r\\n)(?=(?:\\n|\\r))"
#     new_text = re.sub(pattern, "", text)
#     return new_text

