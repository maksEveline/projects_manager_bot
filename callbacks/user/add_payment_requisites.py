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
from keyboards.user.user_inline import get_cancel_menu, get_back_to_project_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


class AddPaymentRequisites(StatesGroup):
    requisites = State()
    confirm = State()


@router.callback_query(F.data.startswith("add_payment_requisites_"))
async def add_payment_requisites(callback: CallbackQuery, state: FSMContext, bot: Bot):
    project_id = callback.data.split("add_payment_requisites_")[-1]
    await state.update_data({"project_id": project_id})
    await state.set_state(AddPaymentRequisites.requisites)

    msg = await bot.edit_message_text(
        text="📋 Напишите реквизиты для оплаты",
        reply_markup=await get_cancel_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )

    await state.update_data({"msg_id": msg.message_id})


@router.message(AddPaymentRequisites.requisites)
async def add_payment_requisites_process(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    project_id = data.get("project_id")
    requisites = message.html_text

    await state.update_data({"requisites": requisites})

    await bot.delete_message(
        chat_id=message.from_user.id, message_id=message.message_id
    )

    kb = [
        [
            InlineKeyboardButton(
                text="✅ Да",
                callback_data=f"confirm_requisites_payment_{project_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="❌ Нет",
                callback_data=f"project_{project_id}",
            ),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text=f"⁉️ Вы точно хотите добавить эти реквизиты?:\n\n{requisites}",
        chat_id=message.from_user.id,
        message_id=msg_id,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("confirm_requisites_payment_"))
async def confirm_payment_requisites(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    data = await state.get_data()
    project_id = data.get("project_id")
    new_requisites = data.get("requisites")

    is_updated = await db.update_payment_requisites(project_id, new_requisites)

    if is_updated:
        await bot.edit_message_text(
            text="✅ Реквизиты проекта успешно добавлены",
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )

    else:
        await bot.edit_message_text(
            text="❌ Ошибка при добавлении реквизитов",
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )
