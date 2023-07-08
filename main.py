import asyncio
from aiogram import Dispatcher, Bot
from utils.default_commands import set_commands
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from middleware import DbSessionMiddleware
from handlers import echo, user_start, admin, cancel, user_commands
from data.config import BOT_TOKEN, DB_PATH


async def main():
    engine = create_async_engine(url=DB_PATH, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    
    bot = Bot(BOT_TOKEN, parse_mode='HTML')
    
    dp = Dispatcher()
    
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    
    # подключение комманды в /menu 
    await set_commands(bot)
    
    # подключение хендлеров к боту 
    dp.include_router(cancel.router)
    dp.include_router(user_start.router)
    dp.include_router(user_commands.router)
    dp.include_router(admin.router)
    dp.include_router(echo.router)
    
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    
    
        
    
if __name__ == '__main__':
    # executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
    print('Бот запущен')
    asyncio.run(main(), debug=False)
    