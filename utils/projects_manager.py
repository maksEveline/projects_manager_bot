import asyncio
from aiogram import Bot

from data.database import db
from utils.time_utils import format_timestamp, get_timestamp, is_future_time
from utils.json_utils import get_price_per_project


async def projects_manager_func(bot: Bot):
    while True:
        projects = await db.get_projects()

        for project in projects:
            user_id = project["user_id"]
            if project["project_type"] == "fixed":
                formated_date = format_timestamp(
                    float(project["subscription_end_date"])
                )
                is_future = is_future_time(formated_date)

                # если подписка закончилась
                if not is_future:
                    if project["auto_refill"] == 1:  # если включено автопродление
                        user_info = await db.get_user(user_id)
                        price_per_project = get_price_per_project()

                        if float(user_info["balance"]) >= float(
                            price_per_project
                        ):  # если баланс пользователя больше или равен цене за проект
                            await db.deduct_balance(user_id, float(price_per_project))

                            sub_time = 30 * 24  # 30 дней * 24 часа
                            sub_timestamp = get_timestamp(sub_time)

                            is_updated = await db.update_project_subscription_end_date(
                                project["project_id"], sub_timestamp
                            )

                            if is_updated:
                                await bot.send_message(
                                    user_id,
                                    f"🎉 Проект {project['name']} успешно продлен на 30 дней",
                                )
                            else:
                                print(
                                    f"Ошибка при обновлении даты окончания подписки проекта {project['name']}"
                                )
                        else:
                            await bot.send_message(
                                user_id,
                                f"🚨 Недостаточно средств для продления подписки проекта {project['name']}",
                            )
                            await db.update_is_active_project(
                                project["project_id"], False
                            )
                    else:
                        await bot.send_message(
                            user_id,
                            f"🚨 Подписка проекта {project['name']} закончилась, перейдите в настройки проекта и продлите подписку",
                        )
                        await db.update_is_active_project(project["project_id"], False)

        await asyncio.sleep(120)
