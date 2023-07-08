
from aiogram.types import Message
from database.db_commands import * 
from data.text import * 
from aiogram import Router



router = Router(name='echo_commands')
   
    
@router.message()
async def echo_handler(message:Message):
    await message.answer(message.text)