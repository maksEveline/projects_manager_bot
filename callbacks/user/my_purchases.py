from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
)

from data.database import db
from keyboards.user.user_inline import get_back_to_main_menu

router = Router()


@router.callback_query(F.data == "my_purchases")
async def print_my_purchases(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id

    purchases = await db.get_user_purchases(user_id)

    answ_text = "<b>🛍️ Ваши покупки:</b>\n\n"

    if len(purchases) == 0:
        answ_text += "😔 У вас нет купленых товаров"
    else:
        for purchase in purchases:
            date = purchase["date"]
            project_name = purchase["project_name"]
            rate_name = purchase["rate_name"]
            price = purchase["price"]

            answ_text += f"📅 Дата: <b>{date}</b>\n"
            answ_text += f"📽️ Проект: <b>{project_name}</b>\n"
            answ_text += f"🦋 Тариф: <b>{rate_name}</b>\n"
            answ_text += f"🏷️ Цена: <b>{price}$</b>\n\n"

    await bot.edit_message_text(
        text=answ_text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=await get_back_to_main_menu(),
        parse_mode="HTML",
    )
