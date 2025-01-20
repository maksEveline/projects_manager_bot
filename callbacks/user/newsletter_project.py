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

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


class NewsletterProject(StatesGroup):
    text = State()
    image = State()
    confirmation = State()


@router.callback_query(F.data.startswith("newsletter_project_"))
async def newsletter_project(callback: CallbackQuery, state: FSMContext, bot: Bot):
    project_id = callback.data.split("newsletter_project_")[-1]
    await state.update_data({"project_id": project_id})
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="👀 Напишите текст рассылки",
        reply_markup=await get_cancel_menu(),
    )
    await state.update_data({"msg_id": callback.message.message_id})
    await state.set_state(NewsletterProject.text)


@router.message(NewsletterProject.text)
async def newsletter_project_text(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await state.update_data({"text": message.text})
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.edit_message_text(
            text="👀 Отправьте изображение для рассылки\n\nЕсли хотите отправить без изображения, напишите любой текст",
            reply_markup=await get_cancel_menu(),
            chat_id=message.chat.id,
            message_id=data["msg_id"],
        )
        await state.set_state(NewsletterProject.image)
    except Exception as e:
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.edit_message_text(
            text="❌ Некорректный ввод. Попробуйте снова.",
            reply_markup=await get_back_to_main_menu(),
            chat_id=message.chat.id,
            message_id=data["msg_id"],
        )
        return


@router.message(NewsletterProject.image)
async def newsletter_project_image(message: Message, state: FSMContext, bot: Bot):
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
        await state.set_state(NewsletterProject.confirmation)
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
            text=f"{data['text']}",
            reply_markup=keyboard,
            chat_id=message.chat.id,
            message_id=data["msg_id"],
        )
        await state.set_state(NewsletterProject.confirmation)
        await bot.delete_message(message.chat.id, message.message_id)


@router.callback_query(F.data == "send_newsletter", NewsletterProject.confirmation)
async def send_newsletter(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    project_id = data["project_id"]
    subscribers = await db.get_project_subscribers(project_id)

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


@router.callback_query(F.data == "newsletter_cancel", NewsletterProject.confirmation)
async def newsletter_cancel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="❌ Рассылка отменена",
        reply_markup=await get_back_to_main_menu(),
    )
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
