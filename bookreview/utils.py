import re


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


def create_fake_db_data(amount_users=10, amount_reviews=20, amount_books=20):
    """
    Создает фейковые данные для таблиц User, Review, Book
    :param amount_users: количество пользователей
    :param amount_reviews: количество рецензий
    :param amount_books: количество книг
    """
    from bookreview.models import User, Review, Book
    databases = [(User, amount_users),
                 (Book, amount_books),
                 (Review, amount_reviews)]
    for database, amount in databases:
        database.create_fake(amount)
