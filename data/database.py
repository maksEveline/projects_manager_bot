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
                    user_id INTEGER PRIMARY KEY,
                    balance FLOAT DEFAULT 0,
                    first_name TEXT,
                    username TEXT
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
                    name TEXT,
                    link TEXT
                )
            """
            )
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS channel (
                    project_id INTEGER,
                    channel_id INTEGER,
                    name TEXT,
                    link TEXT
                )
            """
            )
            # тарифы
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS rate (
                    project_id INTEGER,
                    rate_id INTEGER PRIMARY KEY,
                    name TEXT,
                    price INTEGER,
                    duration INTEGER,
                    duration_type TEXT DEFAULT 'days',
                    description TEXT
                )
            """
            )
            # покупки
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS purchases (
                    user_id INTEGER,
                    project_id INTEGER,
                    rate_id INTEGER,
                    date TEXT
                )
            """
            )
            await self.db.commit()

            print("База данных инициализирована")
        except Exception as e:
            print(f"Ошибка при инициализации базы данных: {e}")

    async def add_user_if_not_exists(
        self, user_id: int, first_name: str, username: str
    ) -> bool:
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
                    "INSERT INTO users (user_id, first_name, username) VALUES (?, ?, ?)",
                    (user_id, first_name, username),
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
                "INSERT INTO project (name, user_id) VALUES (?, ?)",
                (name, user_id),
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
                "SELECT project_id, name FROM project WHERE user_id = ?",
                (user_id,),
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
                "SELECT chat_id, name, link FROM chat WHERE project_id = ?",
                (project_id,),
            ) as cursor:
                chats = await cursor.fetchall()
                for row in chats:
                    result.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "link": row[2],
                            "type": "chat",
                        }
                    )

            async with self.db.execute(
                "SELECT channel_id, name, link FROM channel WHERE project_id = ?",
                (project_id,),
            ) as cursor:
                channels = await cursor.fetchall()
                for row in channels:
                    result.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "link": row[2],
                            "type": "channel",
                        }
                    )

            return result
        except Exception as e:
            print(f"Ошибка при получении чатов и каналов проекта: {e}")
            return None

    async def delete_project(self, project_id: int) -> bool:
        """
        Удаляет проект и все связанные с ним чаты, каналы и тарифы.

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
                "DELETE FROM rate WHERE project_id = ?", (project_id,)
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

    async def add_chat(
        self, project_id: int, chat_id: int, name: str, link: str
    ) -> bool:
        """
        Добавляет чат в таблицу chat.

        :param project_id: ID проекта
        :param chat_id: ID чата
        :param name: Название чата
        :param link: Ссылка на чат
        :return: True если чат успешно добавлен, False в случае ошибки
        """
        try:
            async with self.db.execute(
                "SELECT 1 FROM chat WHERE project_id = ? AND chat_id = ?",
                (project_id, chat_id),
            ) as cursor:
                if await cursor.fetchone() is not None:
                    return False

            await self.db.execute(
                "INSERT INTO chat (project_id, chat_id, name, link) VALUES (?, ?, ?, ?)",
                (project_id, chat_id, name, link),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении чата: {e}")
            return False

    async def add_channel(
        self, project_id: int, channel_id: int, name: str, link: str
    ) -> bool:
        """
        Добавляет канал в таблицу channel.

        :param project_id: ID проекта
        :param channel_id: ID канала
        :param name: Название канала
        :param link: Ссылка на канал
        :return: True если канал успешно добавлен, False в случае ошибки
        """
        try:
            async with self.db.execute(
                "SELECT 1 FROM channel WHERE project_id = ? AND channel_id = ?",
                (project_id, channel_id),
            ) as cursor:
                if await cursor.fetchone() is not None:
                    return False

            await self.db.execute(
                "INSERT INTO channel (project_id, channel_id, name, link) VALUES (?, ?, ?, ?)",
                (project_id, channel_id, name, link),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении канала: {e}")
            return False

    async def update_rate_name(self, rate_id: int, new_name: str) -> bool:
        """
        Обновляет название тарифа.

        :param rate_id: ID тарифа
        :param new_name: Новое название тарифа
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE rate SET name = ? WHERE rate_id = ?",
                (new_name, rate_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении названия тарифа: {e}")
            return False

    async def update_rate_price(self, rate_id: int, new_price: int) -> bool:
        """
        Обновляет цену тарифа.

        :param rate_id: ID тарифа
        :param new_price: Новая цена тарифа
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE rate SET price = ? WHERE rate_id = ?",
                (new_price, rate_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении цены тарифа: {e}")
            return False

    async def update_rate_duration(
        self, rate_id: int, new_duration: int, duration_type: str
    ) -> bool:
        """
        Обновляет продолжительность тарифа.

        :param rate_id: ID тарифа
        :param new_duration: Новая продолжительность тарифа
        :param duration_type: Тип длительности ('days' или 'hours')
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE rate SET duration = ?, duration_type = ? WHERE rate_id = ?",
                (new_duration, duration_type, rate_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении продолжительности тарифа: {e}")
            return False

    async def get_user(self, user_id: int) -> dict | None:
        """
        Получает информацию о пользователе по его ID.

        :param user_id: ID пользователя
        :return: Словарь с информацией о пользователе или None в случае ошибки
        """
        try:
            async with self.db.execute(
                """
                SELECT 
                    u.user_id, 
                    u.balance, 
                    COUNT(DISTINCT p.project_id) as projects_count
                FROM users u
                LEFT JOIN project p ON u.user_id = p.user_id
                WHERE u.user_id = ?
                GROUP BY u.user_id, u.balance
                """,
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "user_id": row[0],
                        "balance": row[1],
                        "projects_count": row[2],
                    }
                return None
        except Exception as e:
            print(f"Ошибка при получении информации о пользователе: {e}")
            return None

    async def get_item(self, item_id: int, type: str) -> dict | None:
        """
        Получает информацию о чате или канале по ID.

        :param item_id: ID чата или канала
        :param type: Тип элемента ('chat' или 'channel')
        :return: Словарь с информацией о чате/канале или None в случае ошибки
        """
        try:
            if type not in ["chat", "channel"]:
                return None

            table = type
            id_column = f"{type}_id"

            async with self.db.execute(
                f"""
                SELECT {id_column}, name, link, project_id 
                FROM {table} 
                WHERE {id_column} = ?
                """,
                (item_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "link": row[2],
                        "project_id": row[3],
                        "type": type,
                    }
                return None
        except Exception as e:
            print(f"Ошибка при получении информации о {type}: {e}")
            return None

    async def add_rate(
        self,
        project_id: int,
        name: str,
        price: int,
        duration: int,
        description: str,
        duration_type: str = "days",
    ) -> bool:
        """
        Добавляет новый тариф в таблицу rate.

        :param project_id: ID проекта
        :param name: Название тарифа
        :param price: Цена тарифа
        :param duration: Продолжительность тарифа
        :param description: Описание тарифа
        :param duration_type: Тип длительности (days, months, years), по умолчанию days
        :return: True если тариф успешно добавлен, False в случае ошибки
        """
        try:
            async with self.db.execute(
                "SELECT 1 FROM rate WHERE project_id = ? AND name = ?",
                (project_id, name),
            ) as cursor:
                if await cursor.fetchone() is not None:
                    return False

            await self.db.execute(
                """
                INSERT INTO rate (project_id, name, price, duration, description, duration_type)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, name, price, duration, description, duration_type),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении тарифа: {e}")
            return False

    async def get_projectid_by_projectname(
        self, project_name: str, user_id: int
    ) -> int | None:
        """
        Получает ID проекта по его названию и ID пользователя.

        :param project_name: Название проекта
        :param user_id: ID пользователя
        :return: ID проекта или None, если проект не найден
        """
        try:
            async with self.db.execute(
                "SELECT project_id FROM project WHERE name = ? AND user_id = ?",
                (project_name, user_id),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Ошибка при получении ID проекта: {e}")
            return None

    async def get_rates(self, project_id: int) -> list[dict] | None:
        """
        Получает все тарифы проекта.

        :param project_id: ID проекта
        :return: Список словарей с информацией о тарифах или None в случае ошибки
        """
        try:
            async with self.db.execute(
                """
                SELECT rate_id, name, price, duration, description, duration_type
                FROM rate 
                WHERE project_id = ?
                """,
                (project_id,),
            ) as cursor:
                rates = await cursor.fetchall()
                return [
                    {
                        "rate_id": row[0],
                        "name": row[1],
                        "price": row[2],
                        "duration": row[3],
                        "description": row[4],
                        "duration_type": row[5],
                    }
                    for row in rates
                ]
        except Exception as e:
            print(f"Ошибка при получении тарифов проекта: {e}")
            return None

    async def get_rate(self, rate_id: int) -> dict | None:
        """
        Получает информацию о тарифе по его ID.

        :param rate_id: ID тарифа
        :return: Словарь с информацией о тарифе или None в случае ошибки
        """
        try:
            async with self.db.execute(
                """
                SELECT rate_id, project_id, name, price, duration, description, duration_type
                FROM rate 
                WHERE rate_id = ?
                """,
                (rate_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "rate_id": row[0],
                        "project_id": row[1],
                        "name": row[2],
                        "price": row[3],
                        "duration": row[4],
                        "description": row[5],
                        "duration_type": row[6],
                    }
                return None
        except Exception as e:
            print(f"Ошибка при получении информации о тарифе: {e}")
            return None

    async def delete_rate(self, rate_id: int) -> bool:
        """
        Удаляет тариф из таблицы rate.

        :param rate_id: ID тарифа для удаления
        :return: True если удаление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute("DELETE FROM rate WHERE rate_id = ?", (rate_id,))
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении тарифа: {e}")
            return False

    async def update_user_balance(self, user_id: int, amount: float) -> bool:
        """
        Обновляет баланс пользователя, добавляя указанную сумму к текущему балансу.

        :param user_id: ID пользователя
        :param amount: Сумма для добавления (может быть отрицательной для уменьшения баланса)
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении баланса пользователя: {e}")
            return False

    async def get_purchases_by_rate(self, rate_id: int) -> list[dict] | None:
        """
        Получает список покупок для конкретного тарифа.

        :param rate_id: ID тарифа
        :return: Список словарей с информацией о покупках или None в случае ошибки
        """
        try:
            async with self.db.execute(
                """
                SELECT p.user_id, p.project_id, p.rate_id, p.date, u.first_name, u.username
                FROM purchases p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.rate_id = ?
                """,
                (rate_id,),
            ) as cursor:
                purchases = await cursor.fetchall()
                return [
                    {
                        "user_id": row[0],
                        "project_id": row[1],
                        "rate_id": row[2],
                        "date": row[3],
                        "first_name": row[4],
                        "username": row[5],
                    }
                    for row in purchases
                ]
        except Exception as e:
            print(f"Ошибка при получении списка покупок: {e}")
            return None

    async def get_user_purchases(self, user_id: int) -> list[dict] | None:
        """
        Получает историю покупок пользователя.

        :param user_id: ID пользователя
        :return: Список словарей с информацией о покупках или None в случае ошибки
        """
        try:
            async with self.db.execute(
                """
                SELECT 
                    pu.date,
                    p.name as project_name,
                    r.name as rate_name,
                    r.price
                FROM purchases pu
                JOIN project p ON pu.project_id = p.project_id
                JOIN rate r ON pu.rate_id = r.rate_id
                WHERE pu.user_id = ?
                ORDER BY pu.date DESC
                """,
                (user_id,),
            ) as cursor:
                purchases = await cursor.fetchall()
                return [
                    {
                        "date": row[0],
                        "project_name": row[1],
                        "rate_name": row[2],
                        "price": row[3],
                    }
                    for row in purchases
                ]
        except Exception as e:
            print(f"Ошибка при получении истории покупок пользователя: {e}")
            return None


db = Database(DB_PATH)
