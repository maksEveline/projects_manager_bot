import os

from aiogram import F, Bot
from aiogram.types import CallbackQuery
from aiogram.types.input_file import FSInputFile

from keyboards.user.user_inline import get_back_to_project_menu
from data.database import db
from config import DURATION_TYPES

from utils.routers import create_router_with_user_middleware
from utils.time_utils import format_timestamp

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("stats_project_"))
async def stats_project(callback: CallbackQuery, bot: Bot):
    project_id = callback.data.split("stats_project_")[-1]
    rates = await db.get_rates(project_id)

    stats_text = "📊 Статистика по доходам проекта:\n\n"

    total_income = 0
    members_data = []

    for rate in rates:
        dur_type = DURATION_TYPES[rate["duration_type"]]
        purchases = await db.get_purchases_by_rate(rate["rate_id"])
        rate_data = [f"{rate['name']} {rate['duration']} {dur_type}"]

        if purchases:
            total_purchases = len(purchases)
            rate_income = total_purchases * rate["price"]
            total_income += rate_income

            stats_text += (
                f"📃 {rate['name']} {rate['duration']} {dur_type} ({rate['price']}$)\n"
            )
            stats_text += f"👥 Участников: {total_purchases}\n"
            stats_text += f"💰 Доход: {rate_income}$\n"

            # stats_text += "Список покупателей:\n"
            for purchase in purchases:
                username = (
                    purchase["username"] if purchase["username"] else "Нет username"
                )
                # stats_text += f"@{username} ID: <code>{purchase['user_id']}</code> | {purchase['first_name']}\n"
                rate_data.append(
                    f"{purchase['first_name']} (@{username if purchase['username'] else 'Нет username'}) ID: {purchase['user_id']} | {purchase['date']}"
                )
            stats_text += "\n"
        else:
            stats_text += (
                f"📃 {rate['name']} {rate['duration']} {dur_type} ({rate['price']}$)\n"
            )
            stats_text += f"👥 Участников: 0\n"
            stats_text += f"💰 Доход: 0$\n\n"
        members_data.append("\n".join(rate_data))

    stats_text += f"💸 Общий доход: {total_income}$"

    file_content = "\n\n".join(members_data)
    file_path = "members.txt"

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(file_content)

    file = FSInputFile(file_path)

    await bot.send_document(
        chat_id=callback.from_user.id,
        document=file,
        caption="Список участников",
    )

    await bot.edit_message_text(
        text=stats_text,
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=await get_back_to_project_menu(project_id),
        parse_mode="HTML",
    )

    try:
        os.remove(file_path)
    except Exception as e:
        print(e)
