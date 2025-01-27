import os

from aiogram import F, Bot
from aiogram.types import (
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile

from data.database import db
from keyboards.admin.admin_inline import get_admin_menu
from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


@router.callback_query(F.data == "admin_statistics")
async def get_admin_statistic(callback: CallbackQuery, state: FSMContext, bot: Bot):
    statistic = await db.get_statistic()
    projects_statistics = await db.get_projects_statistics()

    # Создаем текстовый файл для записи статистики
    with open("statistics.txt", "w", encoding="utf-8") as f:
        f.write("📊 Статистика проектов:\n\n")
        for project in projects_statistics:
            f.write(f"Проект: {project['project_name']}\n")
            f.write(f"Клиентов: {project['clients_count']}\n")
            f.write(
                f"Владелец: @{project['owner_username']} (ID: {project['owner_id']})\n"
            )
            f.write("\n")

    file = FSInputFile("statistics.txt")
    await bot.send_document(callback.message.chat.id, document=file)

    project_types_text = "\n".join(
        [f"- {type_}: {count}" for type_, count in statistic["project_types"].items()]
    )

    top_users_text = "\n".join(
        [
            f"- {user['first_name']} (@{user['username']}) - {user['balance']} $"
            for user in statistic["top_users_by_balance"]
        ]
    )

    top_projects_text = "\n".join(
        [
            f"- {project['name']} ({project['subscribers']} подписчиков)"
            for project in statistic["top_projects_by_subscribers"]
        ]
    )

    answ_text = f"""
📊 Общая статистика:
➖➖➖➖➖➖➖➖➖➖
👥 Всего пользователей: {statistic["total_users"]}
📁 Всего проектов: {statistic["total_projects"]}
🔄 Активных подписок: {statistic["total_active_subscriptions"]}
💰 Общий баланс: {statistic["total_balance"]:,.2f} $
💵 Сумма покупок: {statistic["total_purchases"]:,.2f} $
🚫 Заблокировано: {statistic["total_blocked_users"]}

📋 Типы проектов:
{project_types_text}

💎 Топ по балансу:
{top_users_text}

🏆 Топ проектов:
{top_projects_text}
"""

    await bot.send_message(
        callback.from_user.id,
        answ_text,
        reply_markup=await get_admin_menu(),
    )

    try:
        os.remove("statistics.txt")
    except Exception as e:
        print(e)
