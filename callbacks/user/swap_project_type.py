from aiogram import F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from data.database import db

from keyboards.user.user_inline import get_back_to_project_menu
from utils.routers import create_router_with_user_middleware
from utils.json_utils import get_price_per_project
from utils.time_utils import get_timestamp

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("switch_to_"))
async def swap_project_type(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user = await db.get_user(callback.from_user.id)
    call_data = callback.data
    project_data = call_data.split("switch_to_")[-1]
    project_id = project_data.split("/")[-1]
    project_info = await db.get_project(project_id)
    new_type = project_data.split("/")[0]

    if new_type == "fixed":
        if float(user["balance"]) < float(get_price_per_project()):
            await bot.edit_message_text(
                text="❌ У вас недостаточно средств на балансе",
                reply_markup=await get_back_to_project_menu(project_id),
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
            )
            return
        kb = [
            [
                InlineKeyboardButton(
                    text="💚 Переключить",
                    callback_data=f"accept_switch_to_fixed/{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌Отмена",
                    callback_data="cancel_method",
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text=f"⁉️ Вы уверены, что хотите переключить проект на фикс цену?\nУ вас с баланса будет списано: {get_price_per_project()} $",
            reply_markup=keyboard,
        )
    else:
        if project_info["payment_type"] != "cryptobot":
            await bot.edit_message_text(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                text="❌ Включите оплату cryptobot для переключения на фикс цену",
                reply_markup=await get_back_to_project_menu(project_id),
            )
            return

        kb = [
            [
                InlineKeyboardButton(
                    text="💚 Переключить",
                    callback_data=f"accept_switch_to_percentage/{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌Отмена",
                    callback_data="cancel_method",
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text="⁉ Вы уверены, что хотите переключить проект на % от дохода?",
            reply_markup=keyboard,
        )


@router.callback_query(F.data.startswith("accept_switch_to_"))
async def accept_switch_to_project(
    callback: CallbackQuery, bot: Bot, state: FSMContext
):
    call_data = callback.data
    project_data = call_data.split("accept_switch_to_")[-1]
    project_id = project_data.split("/")[-1]
    new_type = project_data.split("/")[0]

    if new_type == "fixed":
        await db.update_project_type(project_id, new_type)
        await db.deduct_balance(callback.from_user.id, get_price_per_project())
        await db.update_project_subscription_end_date(
            project_id, get_timestamp(30 * 24)
        )
        await bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text="✅ Проект успешно переключен",
            reply_markup=await get_back_to_project_menu(project_id),
        )
        return

    is_updated = await db.update_project_type(project_id, new_type)
    await db.update_is_active_project(project_id, True)
    if is_updated:
        await bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text="✅ Проект успешно переключен",
            reply_markup=await get_back_to_project_menu(project_id),
        )
    else:
        await bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text="❌ Ошибка при переключении проекта",
            reply_markup=await get_back_to_project_menu(project_id),
        )
