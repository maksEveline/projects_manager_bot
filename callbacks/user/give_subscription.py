from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data.database import db
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu

from utils.routers import create_router_with_user_middleware
from utils.time_utils import get_timestamp

router = create_router_with_user_middleware()


class GiveSubscription(StatesGroup):
    user_id = State()
    rate_id = State()


@router.callback_query(F.data.startswith("give_subscription"))
async def start_give_subscription(callback: CallbackQuery, state: FSMContext, bot: Bot):
    project_id = callback.data.split("_")[2]
    await state.update_data({"project_id": project_id})
    await state.set_state(GiveSubscription.rate_id)

    rates = await db.get_rates(project_id)
    project = await db.get_project(project_id)

    kb = []

    for rate in rates:
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"{rate['name']} - {rate['price']}$",
                    callback_data=f"give_rate_sub_{project_id}_{rate['rate_id']}",
                )
            ]
        )

    kb.append([InlineKeyboardButton(text="Отмена", callback_data="cancel_method")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(
        f"Выберите тариф из проекта {project['name']}", reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("give_rate_sub"))
async def give_rate_sub(callback: CallbackQuery, state: FSMContext, bot: Bot):
    rate_id = callback.data.split("_")[3]
    await state.update_data({"rate_id": rate_id})
    await state.set_state(GiveSubscription.user_id)
    await state.update_data({"msg_id": callback.message.message_id})

    await callback.message.edit_text(
        "Напишите user_id пользователя, которому вы хотите выдать подписку",
        reply_markup=await get_cancel_menu(),
    )


@router.message(GiveSubscription.user_id)
async def give_rate_sub_user_id(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    project_id = data["project_id"]
    rate_id = data["rate_id"]
    rate_info = await db.get_rate(rate_id)

    try:
        user_id = int(message.text)
        user = await db.get_user(user_id)

        if user is None:
            await message.answer("Пользователь не найден")
            return

        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.add_user_purchase(user_id, project_id, rate_id, now_time)

        if rate_info["duration_type"] == "hours":
            sub_time = rate_info["duration"]
        elif rate_info["duration_type"] == "days":
            sub_time = rate_info["duration"] * 24

        sub_timestamp = get_timestamp(sub_time)

        await db.add_active_subscriptions(
            user_id, project_id, rate_id, date=sub_timestamp, hourses=sub_time
        )

        await state.update_data({"user_id": user_id})

        await bot.edit_message_text(
            text=f"Подписка выдана пользователю {user['user_id']}",
            chat_id=message.chat.id,
            message_id=data["msg_id"],
            reply_markup=await get_back_to_main_menu(),
        )
        await bot.delete_message(message.chat.id, message.message_id)

        await state.clear()

    except ValueError:
        await message.answer(
            "Введите корректный user_id", reply_markup=await get_cancel_menu()
        )
