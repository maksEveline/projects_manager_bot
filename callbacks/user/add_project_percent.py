from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data.database import db
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu
from config import ADMIN_IDS

from utils.routers import create_router_with_user_middleware
from utils.time_utils import get_timestamp

router = create_router_with_user_middleware()


class AddProjectPercent(StatesGroup):
    name = State()


@router.callback_query(F.data == "add_project_percent")
async def add_percent_project(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user = await db.get_user(callback.from_user.id)

    msg = await bot.edit_message_text(
        text="📋 Напишите название проекта",
        reply_markup=await get_cancel_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )

    await state.update_data({"msg_id": msg.message_id})

    await state.set_state(AddProjectPercent.name)


@router.message(AddProjectPercent.name)
async def add_percent_project_process_name(
    message: Message, state: FSMContext, bot: Bot
):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    project_name = message.text

    sub_time = 9999 * 24  # 30 дней * 24 часа
    sub_timestamp = get_timestamp(sub_time)

    is_added = await db.add_project(
        project_name,
        message.from_user.id,
        project_type="percentage",
        project_sub_end=sub_timestamp,
    )

    if is_added:
        project_id = await db.get_projectid_by_projectname(
            project_name, message.from_user.id
        )
        await db.add_rate(
            project_id=project_id,
            name="Базовый",
            price=5,
            duration=30,
            description="Описание тарифа",
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f"Пользователь {message.from_user.id} ({message.from_user.full_name}) добавил проект {project_name}",
                )
            except:
                pass
        await bot.edit_message_text(
            text="🎉 Проект успешно добавлен",
            reply_markup=await get_back_to_main_menu(),
            chat_id=message.from_user.id,
            message_id=msg_id,
        )
    else:
        await bot.edit_message_text(
            text="❌ Проект с таким названием уже у вас есть",
            reply_markup=await get_back_to_main_menu(),
            chat_id=message.from_user.id,
            message_id=msg_id,
        )

    await state.clear()
    await bot.delete_message(
        chat_id=message.from_user.id, message_id=message.message_id
    )
