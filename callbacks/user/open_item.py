from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.user.user_inline import get_back_to_project_menu
from data.database import db

router = Router()


@router.callback_query(F.data.startswith("item_"))
async def open_item(callback: CallbackQuery, state: FSMContext, bot: Bot):
    item_data = callback.data
    item_type = "chat" if "chat" in item_data else "channel"
    item_id = callback.data.split("_")[-1]
    item = await db.get_item(item_id, item_type)

    msg_text = f"<b>📛 Название: {item['name']}</b>\n\n"
    msg_text += f"<b>🆔 ID: {item['id']}</b>\n"
    msg_text += f"<b>🔗 Ссылка: {item['link']}</b>\n"
    msg_text += f"<b>👷 Проект: №{item['project_id']}</b>"

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=msg_text,
        reply_markup=await get_back_to_project_menu(item["project_id"]),
        parse_mode="HTML",
    )
