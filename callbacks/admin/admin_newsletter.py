import os
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.input_file import FSInputFile

from data.database import db
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu

from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


class AdminNewsletter(StatesGroup):
    peoples = State()
    text = State()
    image = State()
    confirmation = State()


@router.callback_query(F.data == "admin_newsletter")
async def open_admin_newsletter(callback: CallbackQuery, state: FSMContext, bot: Bot):
    kb = [
        [
            InlineKeyboardButton(
                text="Овнеры проектов", callback_data="admin_newsletter_owners"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Все пользователи", callback_data="admin_newsletter_all"
            ),
        ],
        [
            InlineKeyboardButton(text="Отмена", callback_data="cancel_method"),
        ],
    ]

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Выберите кого рассылать",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )
    await state.set_state(AdminNewsletter.peoples)


@router.callback_query(AdminNewsletter.peoples, F.data.startswith("admin_newsletter_"))
async def admin_newsletter_peoples(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    picked_peoples = callback.data.split("_")[-1]
    await state.update_data({"picked_peoples": picked_peoples})
    await state.update_data({"msg_id": callback.message.message_id})
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="👀 Напишите текст рассылки",
        reply_markup=await get_cancel_menu(),
    )
    await state.set_state(AdminNewsletter.text)


@router.message(AdminNewsletter.text)
async def admin_newsletter_text(message: Message, state: FSMContext, bot: Bot):
    await state.update_data({"text": message.text})
    await bot.delete_message(message.chat.id, message.message_id)

    data = await state.get_data()
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["msg_id"],
        text="👀 Прикрепите изображение\nИли напипишите любой текст если не хотите с изображением",
        reply_markup=await get_cancel_menu(),
    )

    await state.set_state(AdminNewsletter.image)


@router.message(AdminNewsletter.image)
async def admin_newsletter_image(message: Message, state: FSMContext, bot: Bot):
    if message.photo:
        data = await state.get_data()
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        downloads_dir = "downloads"
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        file_path = os.path.join(downloads_dir, f"{photo.file_id}.jpg")
        await bot.download_file(file.file_path, file_path)
        await bot.delete_message(message.chat.id, message.message_id)

        await state.update_data({"file_path": file_path})

        kb = [
            [
                InlineKeyboardButton(
                    text="✅ Отправить", callback_data="send_newsletter"
                )
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="newsletter_cancel")],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=FSInputFile(file_path),
            caption=data["text"],
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        await bot.delete_message(message.chat.id, data["msg_id"])
        await state.set_state(AdminNewsletter.confirmation)
    else:
        data = await state.get_data()
        await state.update_data({"file_path": None})

        kb = [
            [
                InlineKeyboardButton(
                    text="✅ Отправить", callback_data="send_newsletter"
                )
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="newsletter_cancel")],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

        await bot.edit_message_text(
            text=f"{data['text']}\n\nCategory: {data['picked_peoples']}",
            reply_markup=keyboard,
            chat_id=message.chat.id,
            message_id=data["msg_id"],
        )
        await state.set_state(AdminNewsletter.confirmation)
        await bot.delete_message(message.chat.id, message.message_id)


@router.callback_query(F.data == "send_newsletter", AdminNewsletter.confirmation)
async def admin_send_newsletter(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    picked_peoples = data["picked_peoples"]
    subscribers = []
    if picked_peoples == "owners":
        subscribers = await db.get_owners()
    elif picked_peoples == "all":
        subscribers = await db.get_all_users()

    valid = 0
    invalid = 0
    for subscriber in subscribers:
        try:
            if data["file_path"]:
                await bot.send_photo(
                    chat_id=subscriber,
                    photo=FSInputFile(data["file_path"]),
                    caption=data["text"],
                )
            else:
                await bot.send_message(
                    chat_id=subscriber,
                    text=data["text"],
                )
            valid += 1
        except Exception as e:
            invalid += 1

    await state.clear()

    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"✅ Рассылка отправлена <code>{valid}</code> пользователям\n❌ Не удалось отправить рассылку <code>{invalid}</code> пользователям",
        reply_markup=await get_back_to_main_menu(),
        parse_mode="HTML",
    )
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@router.callback_query(F.data == "newsletter_cancel", AdminNewsletter.confirmation)
async def admin_newsletter_cancel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="❌ Рассылка отменена",
        reply_markup=await get_back_to_main_menu(),
    )
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
