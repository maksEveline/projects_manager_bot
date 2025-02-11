from aiogram import F, Bot
from aiogram.types import CallbackQuery
from aiogram.types.input_file import FSInputFile
import asyncio
import pytz
from datetime import datetime

from data.database import db
from keyboards.admin.admin_inline import get_admin_menu
from utils.routers import create_router_with_admin_middleware

from config import DB_PATH, ADMIN_IDS

router = create_router_with_admin_middleware()


@router.callback_query(F.data == "make_backup")
async def make_backup(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    db_file = FSInputFile(DB_PATH)

    await bot.send_document(callback.from_user.id, db_file)

    await bot.send_message(
        callback.from_user.id,
        "Бекапы",
        reply_markup=await get_admin_menu(),
    )


async def make_daily_backup(bot: Bot):
    kyiv_tz = pytz.timezone("Europe/Kiev")

    while True:
        now = datetime.now(kyiv_tz)

        target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if now >= target_time:
            target_time = target_time.replace(day=target_time.day + 1)

        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        db_file = FSInputFile(DB_PATH)

        for admin_id in ADMIN_IDS:
            try:
                await bot.send_document(
                    admin_id,
                    db_file,
                    caption=f"Ежедневный бекап базы данных от {target_time.strftime('%Y-%m-%d %H:%M')}",
                )
            except Exception as e:
                print(f"Ошибка при отправке бекапа админу {admin_id}: {e}")
