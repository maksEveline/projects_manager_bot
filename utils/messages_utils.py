from aiogram import Bot

from config import ADMIN_IDS


async def send_admins_message(bot: Bot, message: str):
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, message, parse_mode="HTML")
