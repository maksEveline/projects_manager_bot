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


# print(is_future_time("2025-02-11 23:20:17"))
