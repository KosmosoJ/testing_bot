from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from data.text import TEST_COMMAND, START_COMMAND

async def set_commands(bot:Bot):
    commands = [
        BotCommand(command='tests', description=TEST_COMMAND),
        BotCommand(command='start', description=START_COMMAND),
    ]
    
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
    