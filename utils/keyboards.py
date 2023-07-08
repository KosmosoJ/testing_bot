from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import random


# Клавиатура. Создание клаивиатуры для тестов
async def create_test_kb(items):
    """ Создать клавиатуру тестов """
    
    btns = []
    for item in items:
        btns.append([KeyboardButton(text=item.title)])
    select_kb = ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True, input_field_placeholder='Выберите тест')
    return select_kb

# Клавиатура. Создание клаивиатуры для вопросов
async def create_question_kb(items):
    """ Создать клавиатуру вопросов """
    
    btns = []
    for item in items:
        btns.append([KeyboardButton(text=item.question)])
    select_kb = ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True, input_field_placeholder='Выберите вопрос')
    return select_kb

async def create_answers_kb(items):
    """ Создать клавиатуру ответов """
    
    btns = []
    for item in items:
        btns.append([KeyboardButton(text=item.answer)])
    random.shuffle(btns)
    select_kb = ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True,input_field_placeholder='Выберите ответ')
    return select_kb