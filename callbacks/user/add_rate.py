from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data.database import db
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


class AddProjectRate(StatesGroup):
    name = State()
    price = State()
    duration = State()
    duration_type = State()


@router.callback_query(F.data.startswith("add_rate_"))
async def start_add_rate(callback: CallbackQuery, state: FSMContext, bot: Bot):
    project_id = callback.data.split("add_rate_")[-1]
    await state.update_data(
        {"project_id": project_id, "msg_id": callback.message.message_id}
    )

    await bot.edit_message_text(
        text="📋 Напишите название тарифа",
        reply_markup=await get_cancel_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )

    await state.set_state(AddProjectRate.name)


@router.message(AddProjectRate.name)
async def add_rate_process_name(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    rate_name = message.text

    await bot.edit_message_text(
        text="📋 Напишите цену тарифа в $",
        reply_markup=await get_cancel_menu(),
        chat_id=message.from_user.id,
        message_id=msg_id,
    )

    await bot.delete_message(
        chat_id=message.from_user.id, message_id=message.message_id
    )
    await state.set_state(AddProjectRate.price)
    await state.update_data({"rate_name": rate_name})


@router.message(AddProjectRate.price)
async def add_rate_process_price(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("msg_id")

    try:
        rate_price = float(message.text)

        kb = [
            [
                InlineKeyboardButton(text="Дни", callback_data=f"set_duration_days"),
                InlineKeyboardButton(text="Часы", callback_data=f"set_duration_hours"),
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_method")],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.edit_message_text(
            text="⏰ Выберите метод подписки",
            reply_markup=keyboard,
            chat_id=message.from_user.id,
            message_id=msg_id,
        )

        await bot.delete_message(
            chat_id=message.from_user.id, message_id=message.message_id
        )

        await state.set_state(AddProjectRate.duration_type)
        await state.update_data({"rate_price": rate_price})

    except ValueError:
        await bot.delete_message(
            chat_id=message.from_user.id, message_id=message.message_id
        )

        await bot.edit_message_text(
            text="❌ Введите корректное число\n\n📋 Напишите цену тарифа",
            reply_markup=await get_cancel_menu(),
            chat_id=message.from_user.id,
            message_id=msg_id,
        )


@router.callback_query(AddProjectRate.duration_type)
async def set_add_dur_type(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    rate_name = data.get("rate_name")
    rate_price = data.get("rate_price")
    project_id = data.get("project_id")
    duration_type = call.data.split("set_duration_")[-1]

    await state.update_data({"duration_type": duration_type})

    if duration_type == "days":
        duration_type = "днях"
    elif duration_type == "hours":
        duration_type = "часах"

    await bot.edit_message_text(
        text=f"📋 Напишите длительность тарифа (в {duration_type})",
        reply_markup=await get_cancel_menu(),
        chat_id=call.from_user.id,
        message_id=msg_id,
    )

    await state.set_state(AddProjectRate.duration)


@router.message(AddProjectRate.duration)
async def add_rate_process_duration(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    rate_name = data.get("rate_name")
    rate_price = data.get("rate_price")
    project_id = data.get("project_id")
    duration_type = data.get("duration_type")

    try:
        rate_duration = int(message.text)
        await bot.delete_message(
            chat_id=message.from_user.id, message_id=message.message_id
        )

        is_added = await db.add_rate(
            project_id, rate_name, rate_price, rate_duration, "", duration_type
        )

        if is_added:
            await bot.edit_message_text(
                text=f"✅ Тариф {rate_name} успешно добавлен",
                reply_markup=await get_back_to_main_menu(),
                chat_id=message.from_user.id,
                message_id=msg_id,
            )

        else:
            await bot.edit_message_text(
                text=f"❌ Ошибка при добавлении тарифа {rate_name}",
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
            text="❌ Введите корректное число\n\n📋 Напишите длительность тарифа (в днях)",
            reply_markup=await get_cancel_menu(),
            chat_id=message.from_user.id,
            message_id=msg_id,
        )
