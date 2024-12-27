import aiosqlite

from config import DB_PATH


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = None

    async def initialize(self):
        """Инициализирует базу данных"""
        try:
            self.db = await aiosqlite.connect(self.db_path)
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY
                )
            """
            )
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS project (
                    project_id INTEGER PRIMARY KEY,
                    name TEXT,
                    user_id INTEGER
                )
            """
            )
            await self.db.commit()
        except Exception as e:
            print(f"Ошибка при инициализации базы данных: {e}")

    async def add_user_if_not_exists(self, user_id: int) -> bool:
        """
        Добавляет user_id в таблицу users, если его там нет.
        Возвращает True, если добавление прошло успешно, иначе False.

        :param user_id: Идентификатор пользователя, который нужно добавить.
        :return: True, если user_id был добавлен, False, если он уже существует.
        """
        try:
            async with self.db.execute(
                "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                result = await cursor.fetchone()

            if result is None:
                await self.db.execute(
                    "INSERT INTO users (user_id) VALUES (?)", (user_id,)
                )
                await self.db.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return False

    async def add_project(self, name: str, user_id: int) -> bool:
        """
        Добавляет новый проект в базу данных.

        :param name: Название проекта
        :param user_id: ID пользователя, создающего проект
        :return: True если проект успешно добавлен, False если проект с таким именем уже существует
        """
        try:
            async with self.db.execute(
                "SELECT 1 FROM project WHERE name = ? AND user_id = ?", (name, user_id)
            ) as cursor:
                if await cursor.fetchone() is not None:
                    return False

            await self.db.execute(
                "INSERT INTO project (name, user_id) VALUES (?, ?)", (name, user_id)
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при создании проекта: {e}")
            return False

    async def get_user_projects(self, user_id: int) -> list[dict] | None:
        """
        Получает все проекты пользователя.

        :param user_id: ID пользователя
        :return: Список словарей с информацией о проектах или None в случае ошибки
        """
        try:
            async with self.db.execute(
                "SELECT project_id, name FROM project WHERE user_id = ?", (user_id,)
            ) as cursor:
                projects = await cursor.fetchall()
                return [{"project_id": row[0], "name": row[1]} for row in projects]
        except Exception as e:
            print(f"Ошибка при получении проектов пользователя: {e}")
            return None


db = Database(DB_PATH)
