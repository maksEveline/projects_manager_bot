from aiogram import F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data.database import db
from keyboards.admin.admin_inline import get_admin_menu
from keyboards.user.user_inline import get_cancel_menu
from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


class ChangeBalance(StatesGroup):
    user_id = State()
    balance = State()


@router.callback_query(F.data == "change_balance")
async def change_balance(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(
        callback.from_user.id,
        "Напишите user_id пользователя или <b>username без @</b>, которому вы хотите изменить баланс",
        reply_markup=await get_cancel_menu(),
        parse_mode="HTML",
    )
    await state.set_state(ChangeBalance.user_id)


@router.message(ChangeBalance.user_id)
async def change_balance(message: Message, state: FSMContext, bot: Bot):
    try:
        user_id = int(message.text)
    except ValueError:
        user_id = await db.get_userid_by_username(message.text.lower())
        if user_id is None:
            await bot.send_message(
                message.from_user.id,
                f"Пользователь {message.text} не найден",
                reply_markup=await get_cancel_menu(),
            )
            return

    await state.update_data({"user_id": user_id})
    user_balance = await db.get_user(user_id)
    if user_balance is None:
        await bot.send_message(
            message.from_user.id,
            "Пользователь не найден",
            reply_markup=await get_cancel_menu(),
        )
        return
    await bot.send_message(
        message.from_user.id,
        f"Введите новый баланс для пользователя {user_id}\nТекущий баланс: {user_balance['balance']}",
    )
    await state.set_state(ChangeBalance.balance)


@router.message(ChangeBalance.balance)
async def change_balance(message: Message, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        user_id = data["user_id"]
        new_balance = float(message.text)
        is_changed = await db.change_user_balance(user_id, new_balance)
        if is_changed:
            await bot.send_message(
                message.from_user.id,
                f"Баланс пользователя {user_id} успешно обновлен",
                reply_markup=await get_admin_menu(),
            )
            await state.clear()
        else:
            await bot.send_message(
                message.from_user.id,
                "Ошибка при обновлении баланса пользователя",
                reply_markup=await get_admin_menu(),
            )
            await state.clear()
    except ValueError:
        await bot.send_message(
            message.from_user.id,
            "Пожалуйста, введите корректное число",
            reply_markup=await get_cancel_menu(),
        )
        return
