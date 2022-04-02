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
