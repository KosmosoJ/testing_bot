from aiogram.types import Message, ReplyKeyboardRemove
from typing import List                        
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

import random

from utils.states.user_states import *
from database.db_commands import * 
from utils.keyboards import create_answers_kb
from .admin import f_ask_tests
from data.text import * 



router = Router(name='users_commands')

@router.message(Command('tests'))
async def user_test_menu(message:Message, state:FSMContext):
    await message.answer('1 - Посмотреть тесты\n'
                         '2 - Пройти тест\n'
                         '3 - Посмотреть пройденные тесты')
    await state.set_state(UserStates.choice)
    
@router.message(Command('states'))
async def send_states(message:Message, state:FSMContext):
    states = await state.get_data()
    print(states)
    
@router.message(UserStates.choice)
async def user_process_menu(message:Message, session:AsyncSession, state:FSMContext):
    if message.text == '1':
        await user_send_tests(message,session,state)
        
    elif message.text == '2':
        await user_select_test(message,session,state)
        
    elif message.text == '3':
        await user_send_completed_tests(message,session,state)
        
    else:
        await message.answer('Не знаю что вы хотели этим сказать.',reply_markup=ReplyKeyboardRemove())
        await state.clear()
        
async def user_send_tests(message:Message, session:AsyncSession ,state:FSMContext):
    """ Вывод тестов. Запрос к бд с выводом тестов в чат"""
    
    tests = await db_get_tests_and_questions(session)
    if tests:
        msg = 'Тесты:\n'
        tests_msg = '\n'.join(test for test in tests)
        await message.answer(msg+tests_msg, reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer('Тесты не найдены.', reply_markup=ReplyKeyboardRemove())
        await state.clear()

async def user_select_test(message:Message, session:AsyncSession, state:FSMContext):
    """ Прохождение теста. Запрос от пользователя теста для прохождения"""
    process_tests = await f_ask_tests(message,session,state)
    if process_tests:
        await state.set_state(UserStates.select_test)
    else:
        await state.clear()
        
@router.message(UserStates.select_test)
async def user_get_test(message:Message, session:AsyncSession, state:FSMContext):
    """ Прохождение теста. Получение вопросов, не пройденных пользователем """
    test = await db_get_test(message, session)
    
    # проверка на существование теста
    if test:
        completed = await db_check_user_completed(message,test,session)
        
        # проверка пройден ли тест пользователем
        if not completed:
            questions = await db_get_uncompleted_questions(test,message,session)
            
            # проверка существуют ли вопросы в тесте
            if questions:
                await state.update_data(questions=questions)
                await state.update_data(test=test)
                await user_start_test(message, session, state)
                
            else:
                await message.answer(f'Для теста <b>{test.title}</b> нет вопросов.',reply_markup=ReplyKeyboardRemove())
                await state.clear()
                
        else:
            await message.answer(f'Вы уже проходили тест <b>{test.title}</b>!',reply_markup=ReplyKeyboardRemove())
            await state.clear()
    else:
        await message.answer(f'Тест <b>{message.text}</b> не найден.')
        await state.clear()
        
async def user_start_test(message:Message, session:AsyncSession, state:FSMContext):
    """ Прохождение теста. Вывод ответа и вопроса пользователю """
    data = await state.get_data()
    questions:List[Question] = data.get('questions')
    test = data.get('test')
    
    if questions:
        random.shuffle(questions)
        question = questions.pop(0)
        answers = await db_get_answers(question, session)
        if answers:
            select_kb = await create_answers_kb(answers)
            await message.answer(f'Вопрос:\n<b>{question.question}</b>', reply_markup=select_kb)
            await state.set_state(UserStates.question)
            
            await state.update_data(answers=answers)
            await state.update_data(question=question)
            await state.update_data(questions=questions)
        else:
            await state.update_data(questions=questions)
            await user_start_test(message,session,state)
        
    # Проверка если вдруг каким-то чудом пользователь снова смог отвечать на вопросы
    elif await db_check_user_complete_test(message,test,session):
        user_complete = await db_set_test_completed(message, test, session)
        if user_complete:
            await message.answer('Вы уже проходили тест!',reply_markup=ReplyKeyboardRemove())
            await state.clear()
        else:
            await message.answer('Вы успешно прошли тест.',reply_markup=ReplyKeyboardRemove())
            await state.clear()
        
    else:
        await message.answer('Вопросы не найдены.',reply_markup=ReplyKeyboardRemove())
        await state.clear()
    
@router.message(UserStates.question)
async def process_user_answer(message:Message, session:AsyncSession, state:FSMContext):
    """ Прохождение теста.  Обработка ответа пользователя """
    
    data = await state.get_data()
    answers = data.get('answers')
    question = data.get('question')
    for answer in answers:
        if answer.answer.lower() == message.text.lower():
            user_answer = await db_set_user_answer(message,question,answer,session)
            await user_start_test(message,session,state)
            return
    else:
        await message.answer(f'<b>{message.text}</b> не в вариантах ответа.')
    
async def user_send_completed_tests(message:Message, session:AsyncSession, state:FSMContext):
    completed_tests = await db_get_completed_tests(message,session)
    if completed_tests:
        msg = 'Пройденные вами тесты:\n'
        tests_msg = '\n'.join(test for test in completed_tests)
        await message.answer(msg+tests_msg, reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer('Вы не прошли ни одного теста!',reply_markup=ReplyKeyboardRemove())
        await state.clear()

