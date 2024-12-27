from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from data.database import db
from keyboards.user.user_inline import get_my_projects_menu

router = Router()


@router.callback_query(F.data == "my_projects")
async def show_my_projects(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    projects = await db.get_user_projects(user_id)
    await bot.edit_message_text(
        text="📋 Выберите проект",
        reply_markup=await get_my_projects_menu(projects),
        chat_id=user_id,
        message_id=callback.message.message_id,
    )
