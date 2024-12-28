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
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS chat (
                    project_id INTEGER,
                    chat_id INTEGER,
                    name TEXT
                )
            """
            )
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS channel (
                    project_id INTEGER,
                    channel_id INTEGER,
                    name TEXT
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

    async def get_project_chats_and_channels(
        self, project_id: int
    ) -> list[dict] | None:
        """
        Получает все чаты и каналы проекта.

        :param project_id: ID проекта
        :return: Список словарей с информацией о чатах и каналах или None в случае ошибки
        """
        try:
            result = []

            async with self.db.execute(
                "SELECT chat_id, name FROM chat WHERE project_id = ?", (project_id,)
            ) as cursor:
                chats = await cursor.fetchall()
                for row in chats:
                    result.append({"id": row[0], "name": row[1], "type": "chat"})

            async with self.db.execute(
                "SELECT channel_id, name FROM channel WHERE project_id = ?",
                (project_id,),
            ) as cursor:
                channels = await cursor.fetchall()
                for row in channels:
                    result.append({"id": row[0], "name": row[1], "type": "channel"})

            return result
        except Exception as e:
            print(f"Ошибка при получении чатов и каналов проекта: {e}")
            return None

    async def delete_project(self, project_id: int) -> bool:
        """
        Удаляет проект и все связанные с ним чаты и каналы.

        :param project_id: ID проекта для удаления
        :return: True если удаление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "DELETE FROM chat WHERE project_id = ?", (project_id,)
            )

            await self.db.execute(
                "DELETE FROM channel WHERE project_id = ?", (project_id,)
            )

            await self.db.execute(
                "DELETE FROM project WHERE project_id = ?", (project_id,)
            )

            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении проекта: {e}")
            return False

    async def get_project(self, project_id: int) -> dict | None:
        """
        Получает информацию о проекте по его ID.

        :param project_id: ID проекта
        :return: Словарь с информацией о проекте или None в случае ошибки
        """
        try:
            async with self.db.execute(
                "SELECT project_id, name, user_id FROM project WHERE project_id = ?",
                (project_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {"project_id": row[0], "name": row[1], "user_id": row[2]}
                return None
        except Exception as e:
            print(f"Ошибка при получении информации о проекте: {e}")
            return None


db = Database(DB_PATH)
