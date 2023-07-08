from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from typing import List                        
from database.db_commands import * 
from data.text import * 
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from utils.filters import IsAdmin
from utils.states.test_creation_state import *
from utils.keyboards import create_test_kb, create_question_kb, create_answers_kb

router = Router(name='admin_commands')
    
    
# /users
# /tests -  /create_test /edit_test  /delete_test
# /questions - /create_question /delete_question /edit_question
# /answers - /crete_answer /edit_answer /delete_answers
    
# Пользователи. Получение всех зарегистрированных пользователей 
# Регистрацию убрал, при необходимости можно включить обратно
# в user_start.py
# @router.message(IsAdmin(), Command('ausers'))
# async def get_users(message:Message, session:AsyncSession):
#     users = await db_get_all_users(message, session)
#     await message.answer(users)
    

# Функция помощник. Запрос от пользователя теста
async def f_ask_tests(message:Message, session:AsyncSession, state:FSMContext):
    """ Вывод тестов из бд в клавиатуру с запросом теста """
    
    tests = await db_get_tests(session)
    if tests:
        select_kb = await create_test_kb(tests)
        await message.answer(f'Выберите тест', reply_markup=select_kb)
        return True
    else:
        await message.answer('Тесты не найдены.')
        return False
    
# Функция помощник. Запрос от пользователя вопроса
async def f_ask_questions(message:Message, session:AsyncSession, state:FSMContext):
    """ Вывод вопросов из дб в клавиатуру с запросом вопроса """

    test = await db_get_test(message, session)
    questions = await db_get_questions(test,session)
    if test:
        if questions:
            select_kb = await create_question_kb(questions)
            await message.answer(f'Выберите вопрос', reply_markup=select_kb)
            await state.update_data(test=test)
            await state.update_data(questions=questions)
            return True
        else:
            await message.answer('Вопросы не найдены.', reply_markup=ReplyKeyboardRemove())
            return False
            
    else:
        await message.answer(f'Тест <b>{message.text}</b> не найден.', reply_markup=ReplyKeyboardRemove())
        return False

async def f_get_question(message,questions):
    for question in questions:
        if question.question.lower() == message.text.lower():        
            return question
    else:
        return False     

    
@router.message(IsAdmin(), Command('ahelp'))
async def admin_help(message:Message):
    await message.answer('Админ-помощь:\n'
                         '/atests - меню для работы с тестами\n'
                         '/aquestions - меню для работы с вопросами\n'
                         '/aanswers - меню для работы с ответами\n')
    
@router.message(IsAdmin(),Command('completed'))
async def completed_users(message:Message, session:AsyncSession):
    completed_tests = await db_admin_get_completed_tests(message,session)
    if completed_tests:
        msg = 'Пройденные тесты:\n'
        tests_msg = '\n'.join(test for test in completed_tests)
        await message.answer(msg+tests_msg, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Вы не прошли ни одного теста!',reply_markup=ReplyKeyboardRemove())


    
# ---------- ТЕСТЫ ---------- #

# Тест. Меню выбора действий
@router.message(IsAdmin(),Command('atests'))
async def process_tests(message:Message, session:AsyncSession, state:FSMContext):
    await message.answer(f'1 - Создать тест\n'
                         '2 - Посмотреть тесты\n'
                         '3 - Редактировать тесты\n'
                         '4 - Удалить тест')
    await state.set_state(TestStates.choice)
    
    
@router.message(TestStates.choice)
async def test_choice(message:Message, session:AsyncSession,state:FSMContext):

    if message.text == '1':
        await ask_test_title(message,session,state)
        
    elif message.text == '2':
        await send_tests(message,session,state)
        
    elif message.text == '3':
        await ask_test(message,session,state)
        
    elif message.text == '4':
        await ask_delete_test(message,session,state)
    else:
        await message.answer('Не знаю что вы хотели этим сказать.')
        await state.clear()

    
# Тесты. Вывод всех созданных тестов
async def send_tests(message:Message, session:AsyncSession, state:FSMContext):
    tests = await db_get_tests(session)
    tests_msg = '\n'.join([test.title for test in tests])
    msg = 'Тесты:\n'
    await message.answer(msg+tests_msg, reply_markup=ReplyKeyboardRemove())
    await state.clear()


# Создание теста. Запрос от пользователя названия теста
async def ask_test_title(message:Message, session:AsyncSession, state:FSMContext):
    await message.answer('Введите название теста')
    await state.set_state(TestStates.get_title)

    
# Создание теста.  Получение названия теста с сохранением в базу данных.
@router.message(TestStates.get_title)
async def get_test_title(message:Message, session:AsyncSession, state:FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer('Тест не может называться <b>"отмена"</b>')
        
    test = await db_register_test(message,session)
    await message.answer(f'Тест <strong>{test.title}</strong> был успешно создан!', parse_mode='HTML')
    await state.clear()
    
# @router.message(IsAdmin(),Command('edit_test'))
async def ask_test(message:Message, session:AsyncSession, state:FSMContext):
    process_tests = await f_ask_tests(message,session,state)
    if process_tests:
        await state.set_state(TestStates.edit_test)
    else:
        await state.clear()

        
# Изменение теста. Получение названия теста для изменения, с запросом нового названия.
@router.message(TestStates.edit_test)
async def get_test_item(message:Message, session:AsyncSession, state:FSMContext):    
    test = await db_get_test(message,session)
    
    try:
        await state.update_data(test=test)
        await message.answer(f'Введите новое название теста для <b>{test.title}</b>', reply_markup=ReplyKeyboardRemove())
        await state.set_state(TestStates.get_test_title)
    except:
        print(test)

# Изменение теста. Сохранение нового названия в бд
@router.message(TestStates.get_test_title)
async def get_new_test_title(message:Message, session:AsyncSession, state:FSMContext):
    new_test_title = message.text
    data = await state.get_data()
    try:
        await db_rename_test(session, data.get('test'), new_test_title)
    except:
        print(data)
    
    await message.answer(f'Тест переименован в <strong>{new_test_title}</strong>', reply_markup=ReplyKeyboardRemove())
    await state.clear()
    
    
# Удаление теста. Запрос у пользователя теста на удаление
async def ask_delete_test(message:Message, session:AsyncSession, state:FSMContext):
    process_tests = await f_ask_tests(message,session,state)
    if process_tests:
        await state.set_state(TestStates.delete_test)
    else:
        await state.clear()
    

# Удаление теста. Получение + удаление теста
@router.message(TestStates.delete_test)
async def delete_test(message:Message, session:AsyncSession, state:FSMContext):
    test = await db_get_test(message,session)
    if test:
        test_title = test.title
        await db_delete_item(test, session)
        await message.answer(f'Тест "<strong>{test_title}</strong>" был успешно удален.', reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer(f'Тест <strong>{message.text}</strong> не был найден. Проверьте правильность ввода.')
                

# ---------- ВОПРОСЫ ---------- #

@router.message(IsAdmin() ,Command('aquestions'))
async def call_questions(message:Message, session:AsyncSession, state:FSMContext):
    await message.answer(f'1 - Создать вопрос\n'
                         '2 - Посмотреть вопросы\n'
                         '3 - Редактировать вопрос\n'
                         '4 - Удалить вопрос')
    await state.set_state(QuestionStates.choice)

@router.message(QuestionStates.choice)
async def process_questions(message:Message, session:AsyncSession, state:FSMContext):
    
    if message.text == '1':
        await select_test(message,session,state)
        
    elif message.text == '2':
        await get_questions(message,session,state)
        
    elif message.text == '3':
        await edit_question(message,session,state)
        
    elif message.text == '4':
        await delete_question_ask_task(message,session,state)
    else:
        await message.answer('Не знаю что вы хотели этим сказать.')
        await state.clear()

# Создание вопроса. Выбор теста для добавления вопроса в тест
async def select_test(message:Message, session:AsyncSession, state:FSMContext):
    process_tests = await f_ask_tests(message,session,state)
    if process_tests:
        await state.set_state(QuestionStates.ask_test)
    else:
        await state.clear()


# Создание вопроса. Получение от пользователя теста, запрос названия вопроса
@router.message(QuestionStates.ask_test)
async def ask_question_title(message:Message, session:AsyncSession, state:FSMContext):
    
    test = await db_get_test(message,session)
    if test:
        await message.answer('Введите название вопроса', reply_markup=ReplyKeyboardRemove())
        await state.set_state(QuestionStates.ask_question_title)
        await state.update_data(test=test)
    else:
        await message.answer(f'Тест <b>{message.text}</b> не найден.')
        await state.clear()
    
# Создание вопроса. получение от пользователя вопроса и сохранение в бд
@router.message(QuestionStates.ask_question_title)
async def get_question_title(message:Message, session:AsyncSession, state:FSMContext):
    
    data = await state.get_data()
    test = data.get('test')
    question = await db_register_question(message,session,test)
    await message.answer(f'Вопрос <strong>{question.question}</strong> был успешно создан!', reply_markup=ReplyKeyboardRemove())
    await state.clear()
    
# Удаление вопроса. Запрос от пользователя теста, к которому привязан вопрос
async def delete_question_ask_task(message:Message, session:AsyncSession, state:FSMContext):
    
    process_tests = await ask_test(message,session,state)
    if process_tests:
        await state.set_state(QuestionStates.ask_delete_question)
    else:
        await state.clear()

# Удаление вопроса. Запрос от пользователя вопроса, который будет удален
@router.message(QuestionStates.ask_delete_question)
async def get_question_task(message:Message, session:AsyncSession, state:FSMContext):
    
    process_question = await f_ask_questions(message,session,state)
    if process_question:
        await state.set_state(QuestionStates.delete_task)
    else:
        await state.clear()
        
# Удаление вопроса. удаление вопроса из бд
@router.message(QuestionStates.delete_task)
async def delete_question(message:Message, session:AsyncSession, state:FSMContext):
 
    question_msg = message.text
    data = await state.get_data()
    questions = data.get('questions')
    for question in questions:
        if question.question.lower() == question_msg.lower():
            await db_delete_item(question,session)
            await message.answer(f'Вопрос <strong>{question_msg}</strong> был удален.', reply_markup=ReplyKeyboardRemove())
            await state.clear()
            break
    else:
        await message.answer(f'Вопрос <strong>{question_msg}</strong> не был найден.', reply_markup=ReplyKeyboardRemove())
        await state.clear()    
        
# Изменить вопрос. Получение теста, в котором вопрос
async def edit_question(message:Message, session:AsyncSession, state:FSMContext):
    process_tests = await f_ask_tests(message,session,state)
    if process_tests:
        await state.set_state(QuestionStates.ask_test_edit)
    else:
        await state.clear()
        
# Изменить вопрос. Получение вопроса для изменения
@router.message(QuestionStates.ask_test_edit)
async def ask_edit_question(message:Message, session:AsyncSession, state:FSMContext):
    
    process_question = await f_ask_questions(message,session,state)
    if process_question:
        await state.set_state(QuestionStates.get_question_to_edit)
    else:
        await state.clear()    
            
# Изменить вопрос. Запрос от пользователя нового вопроса
@router.message(QuestionStates.get_question_to_edit)
async def get_edit_question(message:Message, session:AsyncSession, state:FSMContext):
    
    data = await state.get_data()
    questions = data.get('questions')
    for question in questions:
        if question.question.lower() == message.text.lower():
            await message.answer(f'Введите новый вопрос', reply_markup=ReplyKeyboardRemove())
            await state.set_state(QuestionStates.get_new_question)
            await state.update_data(question = question)
            break
    else:
        await message.answer(f'Вопрос <strong>{message.text}</strong> не найден')
        await state.clear()
        
        
# Изменить вопрос. Сохранение вопроса в базу данных.
@router.message(QuestionStates.get_new_question)
async def process_new_question(message:Message, session:AsyncSession, state:FSMContext):
 
    data = await state.get_data()
    question:Question = data.get('question')
    old_question = question.question
    new_question = await db_edit_question(question=question,message=message,session=session)
    if new_question:
        await message.answer(f'Вопрос <strong>{old_question}</strong> изменен на <strong>{message.text}</strong>')
        await state.clear()
    else:
        await message.answer('Не удалось сохранить вопрос в базу данных.')
        
# Получение вопросов. Запрос от пользователя теста
async def get_questions(message:Message, session:AsyncSession, state:FSMContext):
    process_tests = await f_ask_tests(message,session,state)
    
    if process_tests:
        await state.set_state(QuestionStates.get_tests)
    else:
        await state.clear()
        
# Получение вопросов. Вывод всех вопросов привязанных к выбранному тесту
@router.message(QuestionStates.get_tests)
async def send_questions(message:Message, session:AsyncSession, state:FSMContext):
    
    test = await db_get_test(message, session)
    questions = await db_get_questions(test, session)
    msg = 'Вопросы:\n'
    questions_msg = ','.join([question.question for question in questions])
    await message.answer(msg + questions_msg, reply_markup=ReplyKeyboardRemove())
    await state.clear()
    
    
# ---------- ОТВЕТЫ ---------- #

# Ответы. Вывод меню в чат
@router.message(IsAdmin(),Command('aanswers'))
async def answers_menu(message:Message, session:AsyncSession, state:FSMContext):
    await message.answer(f'1 - Добавить ответы\n'
                         '2 - Редактировать ответы\n'
                         '3 - Посмотреть ответы')
    
    await state.set_state(AnswersStates.choice)
    
# Ответы. Обработка выбора пользователя
@router.message(AnswersStates.choice)
async def process_answers(message:Message,session:AsyncSession, state:FSMContext):
    if message.text == '1':
        await answers_ask_test(message,session,state)
    elif message.text == '2':
        await edit_answers(message,session,state)
    elif message.text == '3':
        await answers_send(message, session,state)
    else:
        await message.answer('Не знаю, что вы хотели этим сказать.', reply_markup=ReplyKeyboardRemove())
        await state.clear()

# Создание ответов. Запрос от пользователя теста
async def answers_ask_test(message:Message, session:AsyncSession, state:FSMContext):
    
    process_tasks = await f_ask_tests(message,session,state)
    
    if process_tasks:
        await state.set_state(AnswersStates.get_test)
    else:
        await state.clear()
    
    
# Создание ответов. Запрос от пользователя вопроса
@router.message(AnswersStates.get_test)
async def answers_get_test(message:Message, session:AsyncSession, state:FSMContext):
    
    process_questions = await f_ask_questions(message,session,state)
    if process_questions:
        await state.set_state(AnswersStates.get_question)
    else:
        await state.clear()

       
# Создание ответов. Запрос первого ответа
@router.message(AnswersStates.get_question)
async def answers_get_question(message:Message, session:AsyncSession, state:FSMContext):
    
    data = await state.get_data()
    questions = data.get('questions')
    
    question = await f_get_question(message, questions)
    if question:
        await state.update_data(question=question)
        await message.answer('Введите первый ответ', reply_markup=ReplyKeyboardRemove())
        await state.set_state(AnswersStates.A1)    
    else:
        await message.answer(f'Вопрос <b>{message.text}</b> не был найден.')
        await state.clear()
        
            
# Создание ответов. Запрос второго ответа
@router.message(AnswersStates.A1)
async def answers_get_answer1(message:Message, session:AsyncSession, state:FSMContext):
    
    await state.update_data(a1=message.text)
    await message.answer('Введите второй ответ')
    await state.set_state(AnswersStates.A2)
    
# Создание ответов. Запрос третьего ответа
@router.message(AnswersStates.A2)
async def answers_get_answer1(message:Message, session:AsyncSession, state:FSMContext):
    
    await state.update_data(a2=message.text)
    await message.answer('Введите третий ответ')
    await state.set_state(AnswersStates.A3)
    
# Создание ответов. Запрос третьего ответа
@router.message(AnswersStates.A3)
async def answers_get_answer1(message:Message, session:AsyncSession, state:FSMContext):
    
    await state.update_data(a3=message.text)
    await message.answer('Введите четвертый ответ')
    await state.set_state(AnswersStates.A4)
    
# Создание ответов. Запрос четвертого ответа
@router.message(AnswersStates.A4)
async def answers_get_answer1(message:Message, session:AsyncSession, state:FSMContext):
    
    data = await state.get_data()
    answers = [data.get(f'a{i}') for i in range(1,4)]
    
    answers.append(message.text)
    
    question = data.get('question')
    m_answers = []
    btns = []
    for answer in answers:
        db_answer = await db_check_answer_exists(answer, question,session)
        if not db_answer:
            m_answer = Answer(answer=answer, question_id=question.id, is_correct=False)
        else:
            m_answer = db_answer
        answer = await db_add_to_db(m_answer,message,session)
        btns.append([KeyboardButton(text=answer.answer)])
        m_answers.append(answer)
    select_kb = ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)        
    
    await state.update_data(answers = m_answers)
    await message.answer('Выберите верный вариант ответа',reply_markup=select_kb)
    await state.set_state(AnswersStates.task)
    

# Создание ответов. Сохранение ответов в базу данных.
# Ответы сохраняются в таблицу tasks    
@router.message(AnswersStates.task)
async def create_task(message:Message, session:AsyncSession, state:FSMContext):
    
    data = await state.get_data()
    answers:List = data.get('answers')
    question = data.get('question')
    
    for answer in answers:
        if answer.answer.lower() == message.text.lower():
            correct_answer = answers.pop(answers.index(answer))
            break
    await db_set_correct_answer(message,question,correct_answer,session)    
    await message.answer(f'Ответы для вопроса <b>{question.question}</b> были сохранены!', reply_markup=ReplyKeyboardRemove())

# Редактирование ответа. Запрос от пользователя теста
async def edit_answers(message:Message, session:AsyncSession, state:FSMContext):
    process_tests = await f_ask_tests(message,session,state)
    if process_tests:
        await state.set_state(AnswersStates.edit_answer_get_test)
    else:
        await state.clear()
        
# Редактирование ответа. Получение вопроса
@router.message(AnswersStates.edit_answer_get_test)
async def edit_answers_get_test(message:Message, session:AsyncSession, state:FSMContext):
    
    process_question = await f_ask_questions(message,session,state)
    if process_question:
        await state.set_state(AnswersStates.edit_answer_get_answer)
    else:
        await state.clear()
        
# Редактирование ответа. Запрос от пользователя ответа на редактирование
@router.message(AnswersStates.edit_answer_get_answer)
async def edit_answers_get_answer(message:Message, session:AsyncSession, state:FSMContext):
    
    data = await state.get_data()
    
    test = data.get('test')
    questions = data.get('questions')
    question = await f_get_question(message,questions)
    
    if question:
        answers = await db_get_answers(question, session)
        if answers:
            select_kb = await create_answers_kb(answers)
            await message.answer('Выберите ответ для изменения', reply_markup=select_kb)
            await state.update_data(answers=answers)
            await state.set_state(AnswersStates.edit_answer_get_new_answer)
        else:
            await message.answer(f'Ответы для вопроса <b>{question.question}</b> не были найдены.', reply_markup=ReplyKeyboardRemove())
            await state.clear()
    else:
        await message.answer(f'Вопрос <b>{message.text}</b> не был найден.', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        
# Редактирование ответа. Запрос нового ответа
@router.message(AnswersStates.edit_answer_get_new_answer)
async def edit_answers_ask_new_answer(message:Message, session:AsyncSession, state:FSMContext):
    
    data = await state.get_data()
    answers = data.get('answers')
    for answer in answers:
        if answer.answer.lower() == message.text.lower():
            selected_answer = answer
            await message.answer(f'Введите новый ответ для <b>{selected_answer.answer}</b>', reply_markup=ReplyKeyboardRemove())
            await state.update_data(answer=answer)
            await state.set_state(AnswersStates.edit_answer_process_new_answer)
            break
    else:
        await message.answer(f'Вопрос <b>{message.text}</b> не был найден.', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        
        
# Редактирование ответа. Сохранение ответа в базу данных
@router.message(AnswersStates.edit_answer_process_new_answer)
async def edit_answers_process_neew_answer(message:Message, session:AsyncSession, state:FSMContext):
    
    data = await state.get_data()
    answer = data.get('answer')
    await db_edit_answer(answer,message.text,session)
    
    await message.answer(f'Ответ <b>{message.text}</b> был успешно сохранен ', reply_markup=ReplyKeyboardRemove())
    await state.clear()
            
    
async def answers_send(message:Message, session:AsyncSession, state:FSMContext):
    """ Отправка ответов. Запрос у пользователя теста """
    process_tasks = await f_ask_tests(message,session,state)
    
    if process_tasks:
        await state.set_state(AnswersStates.send_answers_get_test)
    else:
        await state.clear()
        
@router.message(AnswersStates.send_answers_get_test)
async def answers_send_get_test(message:Message, session:AsyncSession, state:FSMContext):
    """ Отправка ответов. Запрос у пользователя вопроса, к которому привязаны ответы """
    process_question = await f_ask_questions(message,session,state)
    if process_question:
        await state.set_state(AnswersStates.send_answers)
    else:
        await state.clear()
        
@router.message(AnswersStates.send_answers)
async def answers_send_process_question(message:Message, session:AsyncSession, state:FSMContext):
    """ Отправка ответов. Вывод ответов в чат """
    data = await state.get_data()
    questions = data.get('questions')
    question = await f_get_question(message, questions)
    
    if question:
        answers = await db_get_answers(question, session)
    else:
        await message.answer(f'Вопрос <b>{message.text}</b> не найден.')
        await state.clear()
        return 
    
    if answers:
        msg = f'Ответы для вопроса <b>{question.question}</b>:\n'
        answers_msg = '\n'.join([answer.answer for answer in answers])
        await message.answer(msg+answers_msg, reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer(f'Ответы для вопроса <b>{question.question}</b> не найдены.', reply_markup=ReplyKeyboardRemove())
        await state.clear()
