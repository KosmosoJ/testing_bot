from aiogram.types import Message
from database.db_commands import * 
from data.text import * 
from aiogram import Router
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from utils.filters import IsAdmin



router = Router(name='user_start')

#Регистрация юзера в боте 
@router.message(CommandStart())
async def command_start(message:Message, session:AsyncSession):
    await message.answer('Здравствуйте!\n'
                         'В данном боте вы можете пройти составленные тесты!\n'
                         'Используйте /tests для просмотра тестов')
        
