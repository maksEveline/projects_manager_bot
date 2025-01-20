from aiogram import F, Bot
from aiogram.types import CallbackQuery

from keyboards.user.user_inline import get_back_to_project_menu
from data.database import db
from config import DURATION_TYPES

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("stats_project_"))
async def stats_project(callback: CallbackQuery, bot: Bot):
    project_id = callback.data.split("stats_project_")[-1]
    rates = await db.get_rates(project_id)

    stats_text = "📊 Статистика по доходам проекта:\n\n"

    total_income = 0
    for rate in rates:
        dur_type = DURATION_TYPES[rate["duration_type"]]
        purchases = await db.get_purchases_by_rate(rate["rate_id"])
        if purchases:
            total_purchases = len(purchases)
            rate_income = total_purchases * rate["price"]
            total_income += rate_income

            stats_text += (
                f"📃 {rate['name']} {rate['duration']} {dur_type} ({rate['price']}$)\n"
            )
            stats_text += f"👥 Участников: {total_purchases}\n"
            stats_text += f"💰 Доход: {rate_income}$\n"

            stats_text += "Список покупателей:\n"
            for purchase in purchases:
                username = (
                    purchase["username"] if purchase["username"] else "Нет username"
                )
                stats_text += f"@{username} ID: <code>{purchase['user_id']}</code> | {purchase['first_name']}\n"
            stats_text += "\n"
        else:
            stats_text += (
                f"📃 {rate['name']} {rate['duration']} {dur_type} ({rate['price']}$)\n"
            )
            stats_text += f"👥 Участников: 0\n"
            stats_text += f"💰 Доход: 0$\n\n"

    stats_text += f"💸 Общий доход: {total_income}$"

    await bot.edit_message_text(
        text=stats_text,
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=await get_back_to_project_menu(project_id),
        parse_mode="HTML",
    )
