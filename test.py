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


# hours = 24
# timestamp = get_timestamp(hours)
# formatted_time = format_timestamp(1739308817.68842)

# print(f"Timestamp через {hours} часов: {timestamp}")
# print(f"Дата и время: {formatted_time}")
