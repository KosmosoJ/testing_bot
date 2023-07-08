from aiogram.types import Message 
from aiogram import F 
from data.config import get_admins
from aiogram.filters import BaseFilter

class IsAdmin(BaseFilter):
    async def __call__(self, message:Message):
        return message.from_user.id in get_admins()
            

    