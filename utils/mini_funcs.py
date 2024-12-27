import asyncio
import random


async def generate_unique_id(start: int = 100000, end: int = 999999) -> int:
    """
    Генерирует уникальный ID в заданном диапазоне

    :param start: Начало диапазона (по умолчанию 100000)
    :param end: Конец диапазона (по умолчанию 999999)
    :return: Уникальный ID
    """
    while True:
        unique_id = random.randint(start, end)
        await asyncio.sleep(0)  # Даем другим корутинам шанс выполниться
        return unique_id
