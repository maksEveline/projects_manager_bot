import asyncio
from aiogram import Bot

from data.database import db
from utils.time_utils import get_timestamp


async def users_subs_checker_func(bot: Bot):
    while True:
        try:
            active_subs = await db.get_active_subscriptions()

            for sub in active_subs:
                user_id = sub["user_id"]
                project_id = sub["project_id"]
                rate_id = sub["rate_id"]
                end_date = sub["date"]
                rate_info = await db.get_rate(rate_id)
                duration_type = rate_info["duration_type"]
                duration = rate_info["duration"]
                project_info = await db.get_project(project_id)

                bot_info = await bot.get_me()
                bot_username = bot_info.username
                paylink = f"https://t.me/{bot_username}?start=project_{project_id}"

                duration_time = 0  # время подписки в часах
                if duration_type == "days":
                    duration_time = int(duration) * 24
                elif duration_type == "hours":
                    duration_time = int(duration)

                current_time = get_timestamp(0)
                time_left = float(end_date) - float(current_time)
                print(
                    f"User: {user_id}, Project: {project_id}, Rate: {rate_id}, Time left: {time_left}"
                )

                if duration_time >= 72:
                    # Проверка для 3 дней
                    if time_left <= 259200 and not await db.check_alert_sent(
                        user_id, project_id, rate_id, "3_days"
                    ):
                        await bot.send_message(
                            user_id,
                            f"❗️Ваша подписка на проект {project_info['name']} истекает через 3 дня.\n🔗Ссылка на покупку:\n{paylink}",
                        )
                        await db.mark_alert_sent(user_id, project_id, rate_id, "3_days")

                if duration_time >= 24:
                    # Проверка для 1 дня
                    if time_left <= 86400 and not await db.check_alert_sent(
                        user_id, project_id, rate_id, "1_day"
                    ):
                        await bot.send_message(
                            user_id,
                            f"❗️Ваша подписка на проект {project_info['name']} истекает через сутки.\n🔗Ссылка на покупку:\n{paylink}",
                        )
                        await db.mark_alert_sent(user_id, project_id, rate_id, "1_day")

                if duration_time > 1:
                    # Проверка для 1 часа
                    if time_left <= 3600 and not await db.check_alert_sent(
                        user_id, project_id, rate_id, "1_hour"
                    ):
                        await bot.send_message(
                            user_id,
                            f"❗️Ваша подписка на проект {project_info['name']} истекает через час.\n🔗Ссылка на покупку:\n{paylink}",
                        )
                        await db.mark_alert_sent(user_id, project_id, rate_id, "1_hour")

        except Exception as e:
            print(f"Ошибка в процессе проверки подписок: {e}")

        await asyncio.sleep(30)
