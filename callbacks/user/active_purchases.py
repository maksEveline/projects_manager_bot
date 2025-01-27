from aiogram import F, Bot
from aiogram.types import CallbackQuery

from data.database import db
from keyboards.user.user_inline import get_back_to_profile_menu

from utils.routers import create_router_with_user_middleware
from utils.time_utils import format_timestamp

router = create_router_with_user_middleware()


@router.callback_query(F.data == "active_purchases")
async def active_purchases(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    active_purchases = await db.get_active_subscriptions()

    answ_text = f"🛍️ Активные покупки:\n\n"

    for purchase in active_purchases:
        try:
            if int(purchase["user_id"]) == int(user_id):
                project_id = purchase["project_id"]
                project_info = await db.get_project(project_id)
                rate_id = purchase["rate_id"]
                rate_info = await db.get_rate(rate_id)
                answ_text += f"🔍 Проект: {project_info['name']}\n"
                answ_text += f"💰 Тариф: {rate_info['name']}\n"
                answ_text += f"🕒 Дата и время окончания: {format_timestamp(float(purchase['date']))}\n"
        except:
            pass

    await bot.edit_message_text(
        text=answ_text,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_back_to_profile_menu(),
    )
