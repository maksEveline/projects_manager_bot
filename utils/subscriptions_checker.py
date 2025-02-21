import asyncio
from aiogram import Bot
from data.database import db
from utils.time_utils import format_timestamp, is_future_time


async def checker_func(bot: Bot):
    while True:
        subscriptions = await db.get_active_subscriptions()
        groups = {}
        for sub in subscriptions:
            key = (sub["user_id"], sub["project_id"])
            groups.setdefault(key, []).append(sub)
        for (user_id, project_id), subs in groups.items():
            active_subs = [
                s for s in subs if is_future_time(format_timestamp(float(s["date"])))
            ]
            expired_subs = [
                s
                for s in subs
                if not is_future_time(format_timestamp(float(s["date"])))
            ]
            for sub in expired_subs:
                await db.delete_subscription(
                    user_id=sub["user_id"],
                    project_id=sub["project_id"],
                    rate_id=sub["rate_id"],
                    date=sub["date"],
                )
            if not active_subs and expired_subs:
                project_chats = await db.get_project_chats_and_channels(project_id)
                project_info = await db.get_project(project_id)
                owner_id = project_info["user_id"]
                user_info = await db.get_user(user_id)
                try:
                    await bot.send_message(
                        chat_id=owner_id,
                        text=f"🚫 У пользователя {user_info['first_name']} (@{user_info['username']}) закончилась подписка на проект {project_info['name']}",
                    )
                    print(f"User {user_id} unsubscribed from project {project_id}")
                    ...
                except Exception as e:
                    # print(e)
                    ...
                for chat in project_chats:
                    # await bot.ban_chat_member(chat["id"], user_id)
                    print(f"Unsubscribing user {user_id} from project {project_id}")
        await asyncio.sleep(30)
