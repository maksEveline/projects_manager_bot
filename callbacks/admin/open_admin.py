from aiogram import F, Bot
from aiogram.types import Message, CallbackQuery
from utils.routers import create_router_with_admin_middleware
from keyboards.admin.admin_inline import get_admin_menu

router = create_router_with_admin_middleware()


@router.message(F.text == "/admin")
async def open_admin(message: Message, bot: Bot):
    await bot.delete_message(message.chat.id, message.message_id)

    await bot.send_message(
        message.from_user.id,
        "Вы вошли в админку",
        reply_markup=await get_admin_menu(),
    )


@router.callback_query(F.data == "admin_menu")
async def admin_menu(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await bot.send_message(
        callback.from_user.id,
        "Вы вошли в админку",
        reply_markup=await get_admin_menu(),
    )
