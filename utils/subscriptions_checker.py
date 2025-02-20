import asyncio
from aiogram import Bot

from data.database import db
from utils.time_utils import format_timestamp, is_future_time


async def checker_func(bot: Bot):
    while True:
        subscriptions = await db.get_active_subscriptions()

        for subscription in subscriptions:
            formated_date = format_timestamp(float(subscription["date"]))
            is_future = is_future_time(formated_date)

            if not is_future:
                project_id = subscription["project_id"]
                project_chats = await db.get_project_chats_and_channels(project_id)
                project_info = await db.get_project(project_id)
                owner_id = project_info["user_id"]
                user_info = await db.get_user(subscription["user_id"])

                await bot.send_message(
                    chat_id=owner_id,
                    text=f"🚫 У пользователя {user_info['first_name']} (@{user_info['username']}) закончилась подписка на проект {project_info['name']}",
                )

                for chat in project_chats:
                    await bot.ban_chat_member(chat["id"], subscription["user_id"])
                    print(
                        f"Unsubscribing user {subscription['user_id']} from project {project_id}"
                    )

                await db.delete_subscription(
                    user_id=subscription["user_id"],
                    project_id=subscription["project_id"],
                    rate_id=subscription["rate_id"],
                    date=subscription["date"],
                )
            else:
                # print(
                #     f"User {subscription['user_id']} is subscribed to project {subscription['project_id']}"
                # )
                ...

        await asyncio.sleep(30)
