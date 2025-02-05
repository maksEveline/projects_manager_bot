from aiogram import F, Bot
from aiogram.types import Message, CallbackQuery
from utils.routers import create_router_with_admin_middleware
from keyboards.admin.admin_inline import get_admin_menu
from keyboards.user.user_inline import get_cancel_menu
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data.database import db


router = create_router_with_admin_middleware()


class BanUser(StatesGroup):
    user_id = State()


class UnbanUser(StatesGroup):
    user_id = State()


@router.callback_query(F.data == "block_user")
async def start_block_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(
        callback.from_user.id,
        "Введите ID пользователя <b>или username без @</b>, который вы хотите заблокировать",
        reply_markup=await get_cancel_menu(),
        parse_mode="HTML",
    )
    await state.set_state(BanUser.user_id)


@router.message(BanUser.user_id)
async def block_user(message: Message, state: FSMContext, bot: Bot):
    try:
        user_id = int(message.text)
    except ValueError:
        user_id = await db.get_userid_by_username(message.text.lower())
        if user_id is None:
            await bot.send_message(
                message.from_user.id,
                f"Пользователь {message.text} не найден",
                reply_markup=await get_admin_menu(),
            )
            return

    is_blocked = await db.add_blocked_user(user_id)
    if is_blocked:
        await bot.send_message(
            message.from_user.id,
            f"Пользователь {user_id} заблокирован",
            reply_markup=await get_admin_menu(),
        )
    else:
        await bot.send_message(
            message.from_user.id,
            "Ошибка при блокировке пользователя",
            reply_markup=await get_admin_menu(),
        )

    await state.clear()


@router.callback_query(F.data == "unblock_user")
async def start_unblock_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(
        callback.from_user.id,
        "Введите ID пользователя <b>или username без @</b>, который вы хотите разблокировать",
        reply_markup=await get_cancel_menu(),
        parse_mode="HTML",
    )
    await state.set_state(UnbanUser.user_id)


@router.message(UnbanUser.user_id)
async def unblock_user(message: Message, state: FSMContext, bot: Bot):
    try:
        user_id = int(message.text)
    except ValueError:
        user_id = await db.get_userid_by_username(message.text.lower())
        if user_id is None:
            await bot.send_message(
                message.from_user.id,
                f"Пользователь {message.text} не найден\n<b>Попробуйте написать ещё раз</b>",
                reply_markup=await get_admin_menu(),
            )
            return

    is_unblocked = await db.delete_blocked_user(user_id)
    if is_unblocked:
        await bot.send_message(
            message.from_user.id,
            f"Пользователь {user_id} разблокирован",
            reply_markup=await get_admin_menu(),
        )
    else:
        await bot.send_message(
            message.from_user.id,
            "Ошибка при разблокировке пользователя",
            reply_markup=await get_admin_menu(),
        )

    await state.clear()
