import pytz
from datetime import datetime, timedelta


def get_timestamp(hours: int) -> float:
    """
    Возвращает timestamp для текущего времени плюс указанное количество часов.
    """
    future_time = datetime.now() + timedelta(hours=hours)
    return future_time.timestamp()


def format_timestamp(timestamp: float) -> str:
    """
    Преобразует timestamp в строку формата "YYYY-MM-DD HH:MM:SS".
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def is_future_time(time_str: str) -> bool:
    """
    Проверяет, находится ли переданное время в будущем.

    :param time_str: строка в формате "YYYY-MM-DD HH:MM:SS"
    :return: True, если указанное время ещё не прошло, иначе False
    """
    given_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return given_time > datetime.now()


def convert_to_timestamp(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())


# print(is_future_time("2025-02-11 23:20:17"))
def format_hours(hours):
    days = hours // 24
    remaining_hours = hours % 24
    if days > 0:
        day_word = (
            "день"
            if days % 10 == 1 and days % 100 != 11
            else (
                "дня" if 2 <= days % 10 <= 4 and not 12 <= days % 100 <= 14 else "дней"
            )
        )
        hour_word = (
            "час"
            if remaining_hours % 10 == 1 and remaining_hours % 100 != 11
            else (
                "часа"
                if 2 <= remaining_hours % 10 <= 4
                and not 12 <= remaining_hours % 100 <= 14
                else "часов"
            )
        )
        return f"{days} {day_word} {remaining_hours} {hour_word}"
    else:
        hour_word = (
            "час"
            if hours % 10 == 1 and hours % 100 != 11
            else (
                "часа"
                if 2 <= hours % 10 <= 4 and not 12 <= hours % 100 <= 14
                else "часов"
            )
        )
        return f"{hours} {hour_word}"


def get_kiev_time():
    kiev_tz = pytz.timezone("Europe/Kiev")
    return datetime.now(kiev_tz).strftime("%Y-%m-%d %H:%M:%S")
