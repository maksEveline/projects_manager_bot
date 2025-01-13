from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
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

    await state.update_data(
        {"project_id": project_id, "msg_id": callback.message.message_id}
    )
    await state.set_state(AddToProject.waiting_for_message)


@router.message(AddToProject.waiting_for_message)
async def process_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    project_id = data.get("project_id")
    msg_text = message.text

    await bot.delete_message(message.chat.id, message.message_id)

    # канал
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
                if bot_member.status == "administrator":
                    # Проверяем, что канал закрытый
                    chat_info = await message.bot.get_chat(forwarded_from)
                    if chat_info.username:
                        await bot.edit_message_text(
                            text="❌ Канал должен быть закрытым. Пожалуйста, закройте канал и попробуйте снова.",
                            chat_id=message.chat.id,
                            message_id=data.get("msg_id"),
                            reply_markup=await get_back_to_project_menu(project_id),
                        )
                        await state.clear()
                        return

                    invite_link = await message.bot.create_chat_invite_link(
                        chat_id=forwarded_from, creates_join_request=True
                    )
                    is_added = await db.add_channel(
                        project_id=project_id,
                        channel_id=forwarded_from,
                        name=message.forward_from_chat.title,
                        link=invite_link.invite_link,
                    )
                    if is_added:
                        await bot.edit_message_text(
                            text=f"✅ Бот успешно добавлен в закрытый канал!\nВот ваша пригласительная ссылка: {invite_link.invite_link}",
                            chat_id=message.chat.id,
                            message_id=data.get("msg_id"),
                            reply_markup=await get_back_to_project_menu(project_id),
                        )
                    else:
                        await bot.edit_message_text(
                            text="❌ Ошибка, такой канал уже добавлен.",
                            chat_id=message.chat.id,
                            message_id=data.get("msg_id"),
                            reply_markup=await get_back_to_project_menu(project_id),
                        )
                else:
                    await bot.edit_message_text(
                        text="❌ Бот не добавлен в канал. Добавьте бота и повторите.",
                        chat_id=message.chat.id,
                        message_id=data.get("msg_id"),
                        reply_markup=await get_back_to_project_menu(project_id),
                    )
            except Exception as e:
                await bot.edit_message_text(
                    text=f"❌ Бот не добавлен в канал или произошла ошибка: {e}",
                    chat_id=message.chat.id,
                    message_id=data.get("msg_id"),
                    reply_markup=await get_back_to_project_menu(project_id),
                )
            await state.clear()
            return

    # группа
    except:
        try:
            chat_id = int(msg_text)

            # Проверяем, добавлен ли бот в группу
            try:
                bot_member = await message.bot.get_chat_member(chat_id, message.bot.id)
                if bot_member.status == "administrator":
                    # Проверяем, что группа закрытая
                    chat_info = await message.bot.get_chat(chat_id)
                    if chat_info.username:
                        await bot.edit_message_text(
                            text="❌ Группа должна быть закрытой. Пожалуйста, закройте группу и попробуйте снова.",
                            chat_id=message.chat.id,
                            message_id=data.get("msg_id"),
                            reply_markup=await get_back_to_project_menu(project_id),
                        )
                        await state.clear()
                        return

                    invite_link = await message.bot.create_chat_invite_link(
                        chat_id=chat_id, creates_join_request=True
                    )
                    chat_name = (
                        message.forward_from_chat.title
                        if message.forward_from_chat
                        else chat_info.title
                    )
                    is_added = await db.add_chat(
                        project_id=project_id,
                        chat_id=chat_id,
                        name=chat_name,
                        link=invite_link.invite_link,
                    )
                    if is_added:
                        await bot.edit_message_text(
                            text=f"✅ Бот успешно добавлен в закрытую группу!\nВот ваша пригласительная ссылка: {invite_link.invite_link}",
                            chat_id=message.chat.id,
                            message_id=data.get("msg_id"),
                            reply_markup=await get_back_to_project_menu(project_id),
                        )
                    else:
                        await bot.edit_message_text(
                            text="❌ Ошибка, такой группа уже добавлена.",
                            chat_id=message.chat.id,
                            message_id=data.get("msg_id"),
                            reply_markup=await get_back_to_project_menu(project_id),
                        )
                else:
                    await bot.edit_message_text(
                        text="❌ Бот не добавлен в группу. Добавьте бота и повторите.",
                        chat_id=message.chat.id,
                        message_id=data.get("msg_id"),
                        reply_markup=await get_back_to_project_menu(project_id),
                    )
            except Exception as e:
                await bot.edit_message_text(
                    text=f"❌ Бот не добавлен в группу или произошла ошибка: {e}",
                    chat_id=message.chat.id,
                    message_id=data.get("msg_id"),
                    reply_markup=await get_back_to_project_menu(project_id),
                )
            await state.clear()
            return

        except ValueError:
            await bot.edit_message_text(
                text="❌ Пожалуйста, отправьте корректный идентификатор чата",
                chat_id=message.chat.id,
                message_id=data.get("msg_id"),
                reply_markup=await get_back_to_project_menu(project_id),
            )
            await state.clear()
            return
