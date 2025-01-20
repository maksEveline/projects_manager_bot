from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.user.user_inline import get_back_to_project_menu
from data.database import db

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("del_item_"))
async def del_item(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    item_data = callback.data.split("_")[-1]
    item_id = item_data.split("/")[0]
    item_type = item_data.split("/")[1]

    is_deleted = await db.delete_item(item_type, item_id)

    if is_deleted:
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=f"✅ Элемент <code>{item_id}</code> удален",
            reply_markup=await get_back_to_project_menu(data["project_id"]),
            parse_mode="HTML",
        )
    else:
        await bot.edit_message_text(
            text="❌ Ошибка при удалении элемента",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(data["project_id"]),
        )
