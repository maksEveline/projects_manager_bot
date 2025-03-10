import aiosqlite

from config import DB_PATH
from utils.time_utils import get_timestamp, get_kiev_time


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
                    username TEXT,
                    max_projects INTEGER DEFAULT 0
                )
            """
            )
            # 0 - выключено, 1 - включено
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS project (
                    project_id INTEGER PRIMARY KEY,
                    name TEXT,
                    user_id INTEGER,
                    project_type TEXT,
                    payment_type TEXT DEFAULT 'cryptobot',
                    auto_refill INTEGER DEFAULT 1, 
                    subscription_end_date TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """
            )
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS payment_requisites (
                    project_id INTEGER,
                    requisites TEXT
                )
            """
            )
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS chat (
                    id INTEGER PRIMARY KEY,
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
                    id INTEGER PRIMARY KEY,
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
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS active_subscriptions (
                    sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    project_id INTEGER,
                    rate_id INTEGER,
                    date TEXT,
                    start_date TEXT,
                    purchase_type TEXT
                )
            """
            )
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS blocked_users (
                    user_id INTEGER
                )
            """
            )
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS buyed_projects (
                    user_id INTEGER,
                    count INTEGER,
                    date TEXT
                )
            """
            )
            await self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS payment_requests (
                    request_id INTEGER,
                    user_id INTEGER,
                    rate_id INTEGER
                )
            """
            )

            await self.db.execute(
                """
            CREATE TABLE IF NOT EXISTS alerts_sent (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                project_id INTEGER,
                rate_id INTEGER,
                alert_type TEXT,
                timestamp TEXT
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

    async def add_project(
        self, name: str, user_id: int, project_type: str, project_sub_end: str
    ) -> bool:
        try:
            async with self.db.execute(
                "SELECT 1 FROM project WHERE name = ? AND user_id = ?", (name, user_id)
            ) as cursor:
                if await cursor.fetchone() is not None:
                    return False

            await self.db.execute(
                """INSERT INTO project 
                   (name, user_id, project_type, payment_type, auto_refill, subscription_end_date) 
                   VALUES (?, ?, ?, 'cryptobot', 0, ?)""",
                (name, user_id, project_type, project_sub_end),
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
                "SELECT project_id, name, project_type FROM project WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                projects = await cursor.fetchall()
                return [
                    {
                        "project_id": row[0],
                        "name": row[1],
                        "project_type": row[2],
                    }
                    for row in projects
                ]
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
                "SELECT project_id, name, user_id, project_type, payment_type, auto_refill, subscription_end_date, is_active FROM project WHERE project_id = ?",
                (project_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "project_id": row[0],
                        "name": row[1],
                        "user_id": row[2],
                        "project_type": row[3],
                        "payment_type": row[4],
                        "auto_refill": row[5],
                        "subscription_end_date": row[6],
                        "is_active": row[7],
                    }
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
                    u.username,
                    u.first_name,
                    u.max_projects,
                    COUNT(DISTINCT p.project_id) as projects_count
                FROM users u
                LEFT JOIN project p ON u.user_id = p.user_id
                WHERE u.user_id = ?
                GROUP BY u.user_id, u.balance, u.max_projects
                """,
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "user_id": row[0],
                        "balance": row[1],
                        "max_projects": row[4],
                        "projects_count": row[5],
                        "first_name": row[3],
                        "username": row[2],
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
                SELECT {id_column}, name, link, project_id, id
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
                        "id_column": row[4],
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

    async def deduct_balance(self, user_id: int, amount: float):
        """Вычитает сумму из баланса пользователя."""
        try:
            async with self.db.execute(
                "SELECT balance FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    print("Пользователь не найден.")
                    return False

                current_balance = result[0]

                if current_balance < amount:
                    print("Недостаточно средств на балансе.")
                    return False

                new_balance = current_balance - amount
                await self.db.execute(
                    "UPDATE users SET balance = ? WHERE user_id = ?",
                    (new_balance, user_id),
                )
                await self.db.commit()
                print(
                    f"Баланс пользователя {user_id} успешно обновлен: {new_balance} (-{amount})"
                )
                return True
        except Exception as e:
            print(f"Ошибка при вычитании суммы из баланса: {e}")
            return False

    async def add_active_subscriptions(
        self,
        user_id: int,
        project_id: int,
        rate_id: int,
        date: str,
        hourses: int = 0,
        payment: str = "undefined",
    ) -> bool:
        """
        Добавляет или обновляет информацию о подписке в таблице active_subscriptions.

        :param user_id: Идентификатор пользователя
        :param project_id: Идентификатор проекта
        :param rate_id: Идентификатор тарифа
        :param date: Дата окончания подписки в формате timestamp
        :param hourses: Количество часов для продления подписки
        :return: True, если операция прошла успешно
        """
        # проверяем существует ли уже активная подписка
        existing_sub = await self.db.execute(
            """
            SELECT date FROM active_subscriptions 
            WHERE user_id = ? AND project_id = ? AND rate_id = ?
            """,
            (user_id, project_id, rate_id),
        )
        result = await existing_sub.fetchone()

        if result:
            # если подписка существует - обновляем дату окончания
            current_date = float(result[0])
            new_date = current_date + (hourses * 3600)  # часы в секунды
            await self.db.execute(
                """
                UPDATE active_subscriptions 
                SET date = ? 
                WHERE user_id = ? AND project_id = ? AND rate_id = ?
                """,
                (str(new_date), user_id, project_id, rate_id),
            )
        else:
            # если подписки нет - создаем новую
            now_time = get_kiev_time()
            await self.db.execute(
                """
                INSERT INTO active_subscriptions (user_id, project_id, rate_id, date, start_date, purchase_type)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, project_id, rate_id, date, now_time, payment),
            )

        await self.db.commit()
        return True

    async def get_project_id_by_chat_id(self, chat_id: int) -> int | None:
        """
        Ищет и возвращает project_id по chat_id или channel_id.
        Если ничего не найдено, возвращает None.
        """
        query_chat = """
            SELECT project_id FROM chat WHERE chat_id = ?
        """
        query_channel = """
            SELECT project_id FROM channel WHERE channel_id = ?
        """

        try:
            async with self.db.execute(query_chat, (chat_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]

            async with self.db.execute(query_channel, (chat_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]

        except Exception as e:
            print(f"Ошибка при поиске project_id: {e}")

        return None

    async def get_user_active_subscriptions(
        self, user_id: int, project_id: int
    ) -> list[dict]:
        """
        Получает список активных подписок пользователя для конкретного проекта
        с подробной информацией о тарифе.

        :param user_id: ID пользователя
        :param project_id: ID проекта
        :return: Список словарей с информацией о подписках
        """
        query = """
            SELECT 
                s.sub_id,
                s.user_id,
                s.project_id,
                s.rate_id,
                s.date,
                r.name as rate_name,
                r.price,
                r.duration,
                r.duration_type,
                r.description,
                p.name as project_name
            FROM active_subscriptions s
            JOIN rate r ON s.rate_id = r.rate_id
            JOIN project p ON s.project_id = p.project_id
            WHERE s.user_id = ? AND s.project_id = ?
        """
        try:
            async with self.db.execute(query, (user_id, project_id)) as cursor:
                rows = await cursor.fetchall()
                subscriptions = [
                    {
                        "sub_id": row[0],
                        "user_id": row[1],
                        "project_id": row[2],
                        "rate_id": row[3],
                        "date": row[4],
                        "rate_name": row[5],
                        "price": row[6],
                        "duration": row[7],
                        "duration_type": row[8],
                        "description": row[9],
                        "project_name": row[10],
                    }
                    for row in rows
                ]
            return subscriptions
        except Exception as e:
            print(f"Ошибка при получении активных подписок: {e}")
            return []

    async def get_active_subscriptions(self):
        cursor = await self.db.execute("SELECT * FROM active_subscriptions")
        rows = await cursor.fetchall()
        await cursor.close()
        return [
            dict(zip([column[0] for column in cursor.description], row)) for row in rows
        ]

    async def delete_subscription(self, user_id, project_id, rate_id, date):
        await self.db.execute(
            """
            DELETE FROM active_subscriptions 
            WHERE user_id = ? AND project_id = ? AND rate_id = ? AND date = ?
            """,
            (user_id, project_id, rate_id, date),
        )

        await self.db.commit()

    async def delete_item(self, item_type: str, item_id: int):
        """Удаляет элемент из таблицы channel или chat по id"""
        table = "channel" if item_type == "channel" else "chat"
        try:
            await self.db.execute(
                f"DELETE FROM {table} WHERE id = ?",
                (item_id,),
            )
            await self.db.commit()
            print(f"Элемент с ID {item_id} успешно удален из таблицы {table}.")
            return True
        except Exception as e:
            print(f"Ошибка при удалении элемента: {e}")
            return False

    async def add_blocked_user(self, user_id: int) -> bool:
        try:
            await self.db.execute(
                "INSERT INTO blocked_users (user_id) VALUES (?)", (user_id,)
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при блокировке пользователя: {e}")
            return False

    async def get_blocked_users(self):
        cursor = await self.db.execute("SELECT user_id FROM blocked_users")
        rows = await cursor.fetchall()
        await cursor.close()
        return [row[0] for row in rows]

    async def delete_blocked_user(self, user_id: int) -> bool:
        try:
            await self.db.execute(
                "DELETE FROM blocked_users WHERE user_id = ?", (user_id,)
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при разблокировке пользователя: {e}")
            return False

    async def change_user_balance(self, user_id: int, new_balance: float) -> bool:
        try:
            await self.db.execute(
                "UPDATE users SET balance = ? WHERE user_id = ?",
                (new_balance, user_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении баланса пользователя: {e}")
            return False

    async def add_user_purchase(
        self, user_id: int, project_id: int, rate_id: int, date: str
    ) -> bool:
        """
        Добавляет информацию о покупке в таблицу purchases.

        :param user_id: ID пользователя
        :param project_id: ID проекта
        :param rate_id: ID тарифа
        :param date: Дата покупки
        :return: True если покупка успешно добавлена, False в случае ошибки
        """
        try:
            await self.db.execute(
                """
                INSERT INTO purchases (user_id, project_id, rate_id, date)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, project_id, rate_id, date),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении покупки: {e}")
            return False

    async def update_subscription_date(self, sub_id: int, new_date: str) -> bool:
        """
        Обновляет дату активной подписки пользователя.

        :param sub_id: ID подписки
        :param new_date: Новая дата подписки
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE active_subscriptions SET date = ? WHERE sub_id = ?",
                (new_date, sub_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении даты подписки: {e}")
            return False

    async def add_max_projects(self, user_id: int, amount: int) -> bool:
        """
        Увеличивает максимальное количество проектов пользователя.

        :param user_id: ID пользователя
        :param amount: Количество проектов для добавления
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE users SET max_projects = max_projects + ? WHERE user_id = ?",
                (amount, user_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении максимального количества проектов: {e}")
            return False

    async def subtract_max_projects(self, user_id: int, amount: int) -> bool:
        """
        Уменьшает максимальное количество проектов пользователя.

        :param user_id: ID пользователя
        :param amount: Количество проектов для вычитания
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            async with self.db.execute(
                "SELECT max_projects FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    return False

                current_max = result[0]
                new_max = current_max - amount

                if new_max < 0:
                    new_max = 0

            await self.db.execute(
                "UPDATE users SET max_projects = ? WHERE user_id = ?",
                (new_max, user_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при вычитании максимального количества проектов: {e}")
            return False

    async def add_buyed_project(self, user_id: int, count: int, date: str) -> bool:
        """
        Добавляет запись о купленных проектах в таблицу buyed_projects.

        :param user_id: ID пользователя
        :param count: Количество купленных проектов
        :param date: Дата покупки
        :return: True если добавление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                """
                INSERT INTO buyed_projects (user_id, count, date)
                VALUES (?, ?, ?)
                """,
                (user_id, count, date),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении записи о купленных проектах: {e}")
            return False

    async def delete_buyed_project(self, user_id: int, count: int, date: str) -> bool:
        """
        Удаляет запись о купленных проектах из таблицы buyed_projects.

        :param user_id: ID пользователя
        :param count: Количество купленных проектов
        :param date: Дата покупки
        :return: True если удаление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                """
                DELETE FROM buyed_projects 
                WHERE user_id = ? AND count = ? AND date = ?
                """,
                (user_id, count, date),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении записи о купленных проектах: {e}")
            return False

    async def get_project_subscribers(self, project_id: int) -> list[int] | None:
        """
        Получает список user_id пользователей с активными подписками для конкретного проекта.

        :param project_id: ID проекта
        :return: Список user_id или None в случае ошибки
        """
        try:
            async with self.db.execute(
                """
                SELECT DISTINCT user_id 
                FROM active_subscriptions 
                WHERE project_id = ?
                """,
                (project_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows] if rows else []
        except Exception as e:
            print(f"Ошибка при получении списка подписчиков проекта: {e}")
            return None

    async def get_owners(self) -> list[int] | None:
        """
        Получает список всех уникальных user_id из таблицы project.

        :return: Список уникальных user_id владельцев проектов или None в случае ошибки
        """
        try:
            async with self.db.execute(
                "SELECT DISTINCT user_id FROM project"
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows] if rows else []
        except Exception as e:
            print(f"Ошибка при получении списка владельцев проектов: {e}")
            return None

    async def get_all_users(self) -> list[int] | None:
        """
        Получает список всех уникальных user_id из таблицы users.

        :return: Список уникальных user_id всех пользователей или None в случае ошибки
        """
        try:
            async with self.db.execute("SELECT DISTINCT user_id FROM users") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows] if rows else []
        except Exception as e:
            print(f"Ошибка при получении списка всех пользователей: {e}")
            return None

    async def update_project_type(self, project_id: int, new_project_type: str) -> bool:
        """
        Обновляет тип проекта.

        :param project_id: ID проекта
        :param new_project_type: Новый тип проекта
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE project SET project_type = ? WHERE project_id = ?",
                (new_project_type, project_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении типа проекта: {e}")
            return False

    async def get_statistic(self) -> dict | None:
        """
        Получает общую статистику для администратора.

        Возвращает словарь, содержащий:
        - Общее количество пользователей
        - Общее количество проектов
        - Общее количество активных подписок
        - Общую сумму на балансах пользователей
        - Общую сумму всех покупок
        - Количество заблокированных пользователей
        - Статистику по типам проектов
        - Топ пользователей по балансу
        - Топ проектов по количеству подписчиков

        :return: Словарь со статистикой или None в случае ошибки
        """
        try:
            async with self.db.execute("SELECT COUNT(*) FROM users") as cursor:
                total_users = (await cursor.fetchone())[0]

            async with self.db.execute("SELECT COUNT(*) FROM project") as cursor:
                total_projects = (await cursor.fetchone())[0]

            async with self.db.execute(
                "SELECT COUNT(*) FROM active_subscriptions"
            ) as cursor:
                total_active_subs = (await cursor.fetchone())[0]

            async with self.db.execute("SELECT SUM(balance) FROM users") as cursor:
                total_balance = (await cursor.fetchone())[0] or 0

            async with self.db.execute(
                """
                SELECT SUM(r.price) 
                FROM purchases p 
                JOIN rate r ON p.rate_id = r.rate_id
            """
            ) as cursor:
                total_purchases = (await cursor.fetchone())[0] or 0

            async with self.db.execute("SELECT COUNT(*) FROM blocked_users") as cursor:
                total_blocked = (await cursor.fetchone())[0]

            async with self.db.execute(
                """
                SELECT project_type, COUNT(*) as count 
                FROM project 
                GROUP BY project_type
            """
            ) as cursor:
                project_types = {row[0]: row[1] for row in await cursor.fetchall()}

            async with self.db.execute(
                """
                SELECT user_id, first_name, username, balance 
                FROM users 
                ORDER BY balance DESC 
                LIMIT 5
            """
            ) as cursor:
                top_users = [
                    {
                        "user_id": row[0],
                        "first_name": row[1],
                        "username": row[2],
                        "balance": row[3],
                    }
                    for row in await cursor.fetchall()
                ]

            async with self.db.execute(
                """
                SELECT 
                    p.project_id,
                    p.name,
                    COUNT(DISTINCT a_sub.user_id) as subscribers
                FROM project p
                LEFT JOIN active_subscriptions a_sub ON p.project_id = a_sub.project_id
                GROUP BY p.project_id, p.name
                ORDER BY subscribers DESC
                LIMIT 5
                """
            ) as cursor:
                top_projects = [
                    {"project_id": row[0], "name": row[1], "subscribers": row[2]}
                    for row in await cursor.fetchall()
                ]

            return {
                "total_users": total_users,
                "total_projects": total_projects,
                "total_active_subscriptions": total_active_subs,
                "total_balance": total_balance,
                "total_purchases": total_purchases,
                "total_blocked_users": total_blocked,
                "project_types": project_types,
                "top_users_by_balance": top_users,
                "top_projects_by_subscribers": top_projects,
            }

        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return None

    async def get_payment_requisites(self, project_id: int) -> str | None:
        """
        Получает реквизиты платежа для проекта.

        :param project_id: ID проекта
        :return: Строка с реквизитами или None, если реквизиты не найдены
        """
        try:
            async with self.db.execute(
                "SELECT requisites FROM payment_requisites WHERE project_id = ?",
                (project_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Ошибка при получении реквизитов платежа: {e}")
            return None

    async def update_payment_requisites(self, project_id: int, requisites: str) -> bool:
        """
        Добавляет или обновляет реквизиты платежа для проекта.

        :param project_id: ID проекта
        :param requisites: Строка с реквизитами
        :return: True если операция прошла успешно, False в случае ошибки
        """
        try:
            async with self.db.execute(
                "SELECT 1 FROM payment_requisites WHERE project_id = ?", (project_id,)
            ) as cursor:
                exists = await cursor.fetchone() is not None

            if exists:
                await self.db.execute(
                    "UPDATE payment_requisites SET requisites = ? WHERE project_id = ?",
                    (requisites, project_id),
                )
            else:
                await self.db.execute(
                    "INSERT INTO payment_requisites (project_id, requisites) VALUES (?, ?)",
                    (project_id, requisites),
                )

            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении реквизитов платежа: {e}")
            return False

    async def update_payment_type(self, project_id: int, payment_type: str) -> bool:
        """
        Обновляет способ оплаты для проекта.

        :param project_id: ID проекта
        :param payment_type: Новый способ оплаты
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE project SET payment_type = ? WHERE project_id = ?",
                (payment_type, project_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении способа оплаты проекта: {e}")
            return False

    async def add_payment_request(
        self, request_id: int, user_id: int, rate_id: int
    ) -> bool:
        """
        Добавляет новый запрос на оплату в таблицу payment_requests.

        :param request_id: ID запроса
        :param user_id: ID пользователя
        :param rate_id: ID тарифа
        :return: True если запрос успешно добавлен, False в случае ошибки
        """
        try:
            await self.db.execute(
                """
                INSERT INTO payment_requests (request_id, user_id, rate_id)
                VALUES (?, ?, ?)
                """,
                (request_id, user_id, rate_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении запроса на оплату: {e}")
            return False

    async def delete_payment_request(self, request_id: int) -> bool:
        """
        Удаляет запрос на оплату из таблицы payment_requests.

        :param request_id: ID запроса для удаления
        :return: True если запрос успешно удален, False в случае ошибки
        """
        try:
            await self.db.execute(
                "DELETE FROM payment_requests WHERE request_id = ?", (request_id,)
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении запроса на оплату: {e}")
            return False

    async def get_payment_request(self, request_id: int) -> dict | None:
        """
        Получает информацию о запросе на оплату по его ID.

        :param request_id: ID запроса
        :return: Словарь с информацией о запросе или None, если запрос не найден
        """
        try:
            async with self.db.execute(
                """
                SELECT request_id, user_id, rate_id
                FROM payment_requests 
                WHERE request_id = ?
                """,
                (request_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {"request_id": row[0], "user_id": row[1], "rate_id": row[2]}
                return None
        except Exception as e:
            print(f"Ошибка при получении информации о запросе на оплату: {e}")
            return None

    async def update_username(self, user_id: int, new_username: str) -> bool:
        """
        Обновляет username пользователя в таблице users.

        :param user_id: ID пользователя
        :param new_username: Новый username пользователя
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE users SET username = ? WHERE user_id = ?",
                (new_username, user_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении username пользователя: {e}")
            return False

    async def get_userid_by_username(self, username: str) -> int | None:
        """
        Получает user_id пользователя по его username.

        :param username: Username пользователя
        :return: ID пользователя или None, если пользователь не найден
        """
        try:
            async with self.db.execute(
                "SELECT user_id FROM users WHERE username = ?", (username,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Ошибка при получении user_id по username: {e}")
            return None

    async def update_auto_refill(self, project_id: int, auto_refill: bool) -> bool:
        """
        Обновляет значение auto_refill для проекта.

        :param project_id: ID проекта
        :param auto_refill: True для включения, False для выключения
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            value = 1 if auto_refill else 0
            await self.db.execute(
                "UPDATE project SET auto_refill = ? WHERE project_id = ?",
                (value, project_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении auto_refill: {e}")
            return False

    async def get_projects(self) -> list[dict] | None:
        """
        Получает информацию о всех проектах.

        :return: Список словарей с информацией о проектах или None в случае ошибки
        """
        try:
            async with self.db.execute(
                """
                SELECT 
                    project_id, 
                    name, 
                    user_id, 
                    project_type, 
                    payment_type, 
                    auto_refill, 
                    subscription_end_date, 
                    is_active
                FROM project
                """
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "project_id": row[0],
                        "name": row[1],
                        "user_id": row[2],
                        "project_type": row[3],
                        "payment_type": row[4],
                        "auto_refill": row[5],
                        "subscription_end_date": row[6],
                        "is_active": row[7],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Ошибка при получении информации о проектах: {e}")
            return None

    async def update_project_subscription_end_date(
        self, project_id: int, new_date: str
    ) -> bool:
        """
        Обновляет дату окончания подписки проекта.

        :param project_id: ID проекта
        :param new_date: Новая дата окончания подписки
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE project SET subscription_end_date = ? WHERE project_id = ?",
                (new_date, project_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении даты окончания подписки проекта: {e}")
            return False

    async def update_is_active_project(self, project_id: int, is_active: bool) -> bool:
        """
        Обновляет статус активности проекта.

        :param project_id: ID проекта
        :param is_active: True для активации, False для деактивации
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            value = 1 if is_active else 0
            await self.db.execute(
                "UPDATE project SET is_active = ? WHERE project_id = ?",
                (value, project_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении статуса активности проекта: {e}")
            return False

    async def check_alert_sent(
        self, user_id: int, project_id: int, rate_id: int, alert_type: str
    ) -> bool:
        query = """
        SELECT 1 FROM alerts_sent
        WHERE user_id = ? AND project_id = ? AND rate_id = ? AND alert_type = ?
        LIMIT 1
        """
        async with self.db.execute(
            query, (user_id, project_id, rate_id, alert_type)
        ) as cursor:
            return await cursor.fetchone() is not None

    async def mark_alert_sent(
        self, user_id: int, project_id: int, rate_id: int, alert_type: str
    ):
        query = """
        INSERT INTO alerts_sent (user_id, project_id, rate_id, alert_type, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """
        timestamp = get_timestamp(0)
        await self.db.execute(
            query, (user_id, project_id, rate_id, alert_type, timestamp)
        )
        await self.db.commit()

    async def get_projects_statistics(self) -> list[dict] | None:
        """
        Получает статистику по всем проектам.

        Возвращает список словарей, содержащий:
        - Название проекта
        - Количество клиентов (активных подписчиков)
        - Username владельца
        - User ID владельца

        :return: Список словарей со статистикой или None в случае ошибки
        """
        try:
            query = """
                SELECT 
                    p.name as project_name,
                    COUNT(DISTINCT a_sub.user_id) as clients_count,
                    u.username as owner_username,
                    p.user_id as owner_id
                FROM project p
                LEFT JOIN active_subscriptions a_sub ON p.project_id = a_sub.project_id
                LEFT JOIN users u ON p.user_id = u.user_id
                GROUP BY p.project_id, p.name, u.username, p.user_id
                ORDER BY clients_count DESC
            """

            async with self.db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "project_name": row[0],
                        "clients_count": row[1],
                        "owner_username": row[2],
                        "owner_id": row[3],
                    }
                    for row in rows
                ]

        except Exception as e:
            print(f"Ошибка при получении статистики проектов: {e}")
            return None

    async def update_subscription_date_by_id(self, sub_id: int, new_date: str) -> bool:
        """
        Обновляет дату подписки по её ID.

        :param sub_id: ID подписки
        :param new_date: Новая дата подписки
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE active_subscriptions SET date = ? WHERE sub_id = ?",
                (new_date, sub_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении даты подписки: {e}")
            return False

    async def update_project_owner(self, project_id: int, owner_id: int) -> bool:
        """
        Обновляет владельца проекта.

        :param project_id: ID проекта
        :param owner_id: ID нового владельца
        :return: True если обновление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                "UPDATE project SET user_id = ? WHERE project_id = ?",
                (owner_id, project_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении владельца проекта: {e}")
            return False

    async def delete_alerts(self, user_id: int, project_id: int, rate_id: int) -> bool:
        """
        Удаляет все записи из таблицы alerts_sent для указанных параметров.

        :param user_id: ID пользователя
        :param project_id: ID проекта
        :param rate_id: ID тарифа
        :return: True если удаление прошло успешно, False в случае ошибки
        """
        try:
            await self.db.execute(
                """
                DELETE FROM alerts_sent 
                WHERE user_id = ? AND project_id = ? AND rate_id = ?
                """,
                (user_id, project_id, rate_id),
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении оповещений: {e}")
            return False

    async def get_username_by_id(self, user_id: int) -> str | None:
        """
        Получает username пользователя по его ID.

        :param user_id: ID пользователя
        :return: Username пользователя или None, если пользователь не найден
        """
        try:
            async with self.db.execute(
                "SELECT username FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Ошибка при получении username по user_id: {e}")
            return None

    async def get_firstname_by_userid(self, user_id: int) -> str | None:
        """
        Получает first_name пользователя по его ID.

        :param user_id: ID пользователя
        :return: First name пользователя или None, если пользователь не найден
        """
        try:
            async with self.db.execute(
                "SELECT first_name FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Ошибка при получении first_name по user_id: {e}")
            return None


db = Database(DB_PATH)
