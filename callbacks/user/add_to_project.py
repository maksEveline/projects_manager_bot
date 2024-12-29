from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from data.database import db
from keyboards.user.user_inline import get_back_to_project_menu

router = Router()


class AddToProject(StatesGroup):
    waiting_for_message = State()


@router.callback_query(F.data.startswith("add_to_project_"))
async def add_to_project(callback: CallbackQuery, bot: Bot, state: FSMContext):
    project_id = callback.data.split("add_to_project_")[-1]
    bot_username = (await bot.get_me()).username
    identy_link = (
        "https://help.send.tg/ru/articles/9820316-как-подключить-частную-группу"
    )

    await bot.edit_message_text(
        text=f"""Чтобы подключить канал, выполните эти действия:

1. Добавьте @{bot_username} в качестве администратора вашего канала или группы.
2. Затем перешлите сюда любое сообщение, отправленное от имени канала. Чтобы подключить группу, пришлите <a href="{identy_link}">идентификатор чата</a>.""",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_back_to_project_menu(project_id),
        parse_mode="HTML",
    )

    await state.set_state(AddToProject.waiting_for_message)


@router.message(AddToProject.waiting_for_message)
async def process_message(message: Message, state: FSMContext):
    try:
        # Проверяем, если сообщение переслано из канала
        is_channel = message.forward_from_chat.type
        if is_channel == "channel":
            forwarded_from = message.forward_from_chat.id

            # Проверяем, добавлен ли бот в канал
            try:
                bot_member = await message.bot.get_chat_member(
                    forwarded_from, message.bot.id
                )
                if bot_member.status in ("administrator", "member"):
                    # Проверяем, что канал закрытый
                    chat_info = await message.bot.get_chat(forwarded_from)
                    if chat_info.username:
                        await message.answer(
                            "❌ Канал должен быть закрытым. Пожалуйста, закройте канал и попробуйте снова."
                        )
                        return

                    # Создаем пригласительную ссылку
                    invite_link = await message.bot.create_chat_invite_link(
                        forwarded_from
                    )
                    await message.answer(
                        f"✅ Бот успешно добавлен в закрытый канал!\nВот ваша пригласительная ссылка: {invite_link.invite_link}"
                    )
                else:
                    await message.answer(
                        "❌ Бот не добавлен в канал. Добавьте бота и повторите."
                    )
            except Exception as e:
                await message.answer(
                    f"❌ Бот не добавлен в канал или произошла ошибка: {e}"
                )
            return

    except:
        msg_text = message.text
        try:
            chat_id = int(msg_text)

            # Проверяем, добавлен ли бот в группу
            try:
                bot_member = await message.bot.get_chat_member(chat_id, message.bot.id)
                if bot_member.status in ("administrator", "member"):
                    # Проверяем, что группа закрытая
                    chat_info = await message.bot.get_chat(chat_id)
                    if chat_info.username:
                        await message.answer(
                            "❌ Группа должна быть закрытой. Пожалуйста, закройте группу и попробуйте снова."
                        )
                        return

                    # Создаем пригласительную ссылку
                    invite_link = await message.bot.create_chat_invite_link(chat_id)
                    await message.answer(
                        f"✅ Бот успешно добавлен в закрытую группу!\nВот ваша пригласительная ссылка: {invite_link.invite_link}"
                    )
                else:
                    await message.answer(
                        "❌ Бот не добавлен в группу. Добавьте бота и повторите."
                    )
            except Exception as e:
                await message.answer(
                    f"❌ Бот не добавлен в группу или произошла ошибка: {e}"
                )
            return

        except ValueError:
            await message.answer(
                "❌ Пожалуйста, отправьте корректный идентификатор чата"
            )
            return
