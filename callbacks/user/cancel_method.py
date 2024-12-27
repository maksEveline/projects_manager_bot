from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.user.user_inline import get_back_to_main_menu

router = Router()


@router.callback_query(F.data == "cancel_method")
async def cancel_method(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.edit_message_text(
        text="⭕️ Вы успешно отменили действие",
        reply_markup=await get_back_to_main_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )
