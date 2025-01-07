from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data.database import db
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu

router = Router()


class TopupBalance(StatesGroup):
    sum = State()


@router.callback_query(F.data == "add_balance")
async def start_topup_balance(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data({"msg_id": callback.message.message_id})

    await bot.edit_message_text(
        text="📋 Напишите сумму пополнения в $",
        reply_markup=await get_cancel_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )

    await state.set_state(TopupBalance.sum)


@router.message(TopupBalance.sum)
async def topup_balance_process_sum(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("msg_id")

    try:
        sum = float(message.text)
        await bot.delete_message(
            chat_id=message.from_user.id, message_id=message.message_id
        )

        is_updated = await db.update_user_balance(
            user_id=message.from_user.id, amount=sum
        )

        if is_updated:
            await bot.edit_message_text(
                text=f"✅ Сумма пополнения: ${sum}",
                reply_markup=await get_back_to_main_menu(),
                chat_id=message.from_user.id,
                message_id=msg_id,
            )
        else:
            await bot.edit_message_text(
                text="❌ Ошибка при пополнении баланса",
                reply_markup=await get_back_to_main_menu(),
                chat_id=message.from_user.id,
                message_id=msg_id,
            )

        await state.clear()

    except ValueError:
        await bot.delete_message(
            chat_id=message.from_user.id, message_id=message.message_id
        )
        await bot.edit_message_text(
            text="❌ Введите корректное число\n\n📋 Напишите сумму пополнения в $",
            reply_markup=await get_cancel_menu(),
            chat_id=message.from_user.id,
            message_id=msg_id,
        )
