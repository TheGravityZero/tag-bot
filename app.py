import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(), override=True)

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
#from handlers.admin_private import admin_router


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
bot.my_admins_list = []


description = """
📍Здесь вы можете получить секретную подборку стильных локаций, в которых сразу же можете идти снимать контент!

Для этого нажмите на кнопку «Начать»
"""




dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(user_group_router)
#dp.include_router(admin_router)



async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()

 
async def on_shutdown(bot):
    print('бот лег')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.set_my_description(description)
    await bot.delete_webhook(drop_pending_updates=True)
    #await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    #await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    

asyncio.run(main())
