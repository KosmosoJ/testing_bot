from sqlalchemy.exc import IntegrityError
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.quiz import * 
from aiogram.types import Message
from datetime import datetime

async def db_add_to_db(item, message:Message, session:AsyncSession):
    """Добавление сущности в бд"""
    
    session.add(item)
    try:
            
        await session.commit()
        await session.refresh(item)
        return item
    except IntegrityError as ex:
        await session.rollback()
        await message.answer('Произошла ошибка.')
        await message.answer(ex)
    
# регистрация юзера
async def db_register_user(message:Message, session:AsyncSession):
    username = message.from_user.username if message.from_user.username else 'хз'
    
    user = User(tg_id=int(message.from_user.id), name=username)
    
    session.add(user)
    
    try:
        await session.commit()
        await session.refresh(user)
        return True
    except IntegrityError:
        await session.rollback()
        return False
    

async def db_get_all_users(message:Message, session:AsyncSession):
    """ получение всех юзеров """
    
    sql = select(User)
    users_sql = await session.execute(sql)
    users = users_sql.scalars()
    
    users_list = '\n'.join([f'{index+1}. {item.tg_id}' for index, item in enumerate(users)])    
    
    return users_list
    

async def db_register_test(message:Message, session:AsyncSession):
    """ Регистрация теста в базу данных """
    
    title = message.text
    test = Test(title=title)

    test = await db_add_to_db(test,message,session)
    return test



async def db_get_tests(session:AsyncSession):
    """ Получение списка всех тестов для вывода в клавиатуру """
    
    sql = select(Test)
    tests_sql = await session.execute(sql)
    tests = tests_sql.scalars()
    tests = [item for _, item in enumerate(tests)]
    
    if tests:
        return tests
    else:
        return None
    

async def db_rename_test(session:AsyncSession, test:Test, new_title):
    """Переименование теста"""
    
    sql = await session.execute(update(Test).where(Test.id == test.id).values(title=new_title))
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
    

async def db_get_test(message:Message ,session:AsyncSession):
    """ Получение одного теста """
    sql =  await session.execute(select(Test).where(Test.title == message.text))
    # test_sql = await session.scalars(sql)
    test = sql.scalars().first()
    return test


async def db_register_question(message:Message, session:AsyncSession, test:Test):
    """Регистрация вопроса в базу данных"""
    
    title = message.text 
    question = Question(test_id=test.id, question=title)
    
    question = await db_add_to_db(question,message,session)
    return question
        

""" удаление сущности из бд"""
async def db_delete_item(item, session:AsyncSession):
    try:
        await session.delete(item)
        await session.commit()
        # await session.refresh(item)
    except IntegrityError:
        await session.rollback()
        

async def db_get_questions(test:Test, session:AsyncSession):
    """ получение списка вопросов по тесту """
    
    sql = await session.execute(select(Question).where(Question.test_id==test.id))
    questions = sql.scalars().all()
    print(questions)
    return questions


async def db_edit_question(question:Question,message:Message, session:AsyncSession):
    """ изменение вопроса в бд"""
    
    sql = await session.execute(update(Question).where(Question.question == question.question).values(question=message.text))
    
    try:
        await session.commit()
        return True
    except IntegrityError:        
        await session.rollback()
        return False
        

async def db_create_answer(message:Message,question, correct, session:AsyncSession):
    """создание ответа в бд"""
    
    answer = Answer(answer=message.text, question_id = question.id, is_correct = correct)
    await db_add_to_db(answer,message,session)
    return answer


async def db_check_answer_exists(user_answer, question:Question, session:AsyncSession):
    """ проверка существует ли ответ в бд"""
    
    sql = await session.execute(select(Answer).where(Answer.answer == user_answer).where(Answer.question_id == question.id))

    answer = sql.scalars().first()
    if answer:
        return answer
    else:
        return False


async def db_set_correct_answer(message:Message, question:Question, correct_answer:Answer, session:AsyncSession):
    """Установка правильного ответа после создания 4х ответов"""
    
    sql_answer = await session.execute(update(Answer).where(Answer.id == correct_answer.id ).where(Answer.question_id == question.id).values(is_correct=True))
    
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        
    

async def db_get_answers(question, session:AsyncSession):
    """ Получение всех ответов привязанных к выбранному вопросу """
    
    sql_task = await session.execute(select(Answer).where(Answer.question_id == question.id).order_by(Answer.id))
    answers = sql_task.scalars().all()

    return answers


async def db_edit_answer(answer, new_answer, session:AsyncSession):
    """ Изменение ответа """
    
    answer_sql = await session.execute(update(Answer).where(Answer.id == answer.id).values(answer=new_answer))
    
    try:
        await session.commit()
        return True
    except IntegrityError:        
        await session.rollback()
        return False
    
async def db_edit_correct_answer(answer, new_answer, session:AsyncSession):
    """ Изменить правильный ответ """
    
    old_answer = await session.execute(update(Answer).where(Answer.id == answer.id).values(is_correct=False))
    new_correct = await session.execute(update(Answer).where(Answer.id == new_answer.id).values(is_correct = True))
    
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
     
     
async def db_get_tests_and_questions(session:AsyncSession):
    """ Получение тестов и количества вопросов"""
    
    sql_tests = await session.execute(select(Test))
    tests = sql_tests.scalars().all()
    
    test_list = []
    for test in tests:
        sql_questions = await session.execute(select(Question).where(Question.test_id == test.id))
        questions = sql_questions.scalars().all()
        if questions:
            test_list.append(f'Тест <b>{test.title}</b> - {len(questions)} вопросов')
        else:
            test_list.append(f'Тест <b>{test.title}</b> - нет вопросов')
            
    return test_list


# select * from questions where questions.id not in (select question_id from user_answers);

async def db_get_uncompleted_questions(test:Test,message:Message, session:AsyncSession):
    """ Получение не пройденных пользователем ответов """
    sql_questions = await session.execute(select(Question).where(Question.test_id == test.id).where(Question.id.not_in(select(UserTestAnswer.question_id)\
        .where(UserTestAnswer.user_id == message.from_user.id))))
    questions = sql_questions.scalars().all()
    return questions


async def db_set_user_answer(message:Message, question:Question, answer:Answer, session:AsyncSession):
    """ Добавление ответа пользователя в базу данных """
    user_answer = UserTestAnswer(user_id=message.from_user.id, question_id=question.id, 
                                 answer_id=answer.id, time=datetime.utcnow())
    user_answer = await db_add_to_db(user_answer, message,session)

    return user_answer


async def db_check_user_complete_test(message:Message, test:Test, session:AsyncSession):
    """ Проверка на завершение пользователем теста """
    sql_questions = await session.execute(select(Question).where(Question.test_id == test.id))
    questions = sql_questions.scalars().all()
    user_answers = []
    for question in questions:
        sql_user_answers = await session.execute(select(UserTestAnswer).where(UserTestAnswer.user_id == message.from_user.id).where(UserTestAnswer.question_id == question.id))
        user_answer = sql_user_answers.scalars().first()
        user_answers.append(user_answer)
        
    if len(questions) == len(user_answers):
        return True
    else:
        return False
    
async def db_check_user_completed(message:Message, test:Test, session:AsyncSession):
    """ Проверка прошел ли пользователь тест"""
    sql_completed = await session.execute(select(UserCompletedTest).where(UserCompletedTest.user_id == message.from_user.id).where(UserCompletedTest.test_id == test.id))
    completed = sql_completed.scalars().first()
    return completed
    
async def db_set_test_completed(message:Message, test, session:AsyncSession):
    """ Добавление пользователя в таблицу завершивших тест """
    sql_completed_test = await session.execute(select(UserCompletedTest).where(UserCompletedTest.user_id == message.from_user.id).where(UserCompletedTest.test_id == test.id))
    completed_test = sql_completed_test.scalars().first()
    if completed_test:
        return True
    else:
        user_completed = UserCompletedTest(user_id = message.from_user.id, test_id = test.id,
                                           username=message.from_user.username if message.from_user.username else None)
        user_completed = await db_add_to_db(user_completed, message, session)
        return False
    
async def db_get_completed_tests(message:Message, session:AsyncSession):
    """ Получение пройденных пользователем тестов и набранных баллов """
    sql_completed_tests = await session.execute(select(UserCompletedTest).where(UserCompletedTest.user_id == message.from_user.id))
    completed_tests = sql_completed_tests.scalars().all()    
    tests = []
    for completed_test in completed_tests:
        question_count = 0
        correct = 0
        
        test = completed_test.test
        
        sql_questions = await session.execute(select(Question).where(Question.test_id == test.id))
        questions = sql_questions.scalars().all()
        question_count += len(questions)
        try:
            for question in questions:
                sql_user_answer = await session.execute(select(UserTestAnswer).where(UserTestAnswer.question_id == question.id))
                user_answer = sql_user_answer.scalars().first()
                if user_answer.answer.is_correct:
                    correct += 1
                    
            item = f'<b>{test.title}</b> - набранные баллы {correct}/{question_count}'
            tests.append(item)
            
        except Exception as ex:
            print(ex)
            
    return tests    

async def db_admin_get_completed_tests(message:Message, session:AsyncSession):
    """ Вывод всех пройденных пользователями тестов """
    sql_completed_tests = await session.execute(select(UserCompletedTest))
    completed_tests = sql_completed_tests.scalars().all()
    users = []
    for completed_test in completed_tests:
        question_count = 0
        correct = 0
        user = f'@{completed_test.username}' if completed_test.username else f'id_{completed_test.user_id}'
        test = completed_test.test
        
        sql_questions = await session.execute(select(Question).where(Question.test_id == test.id))
        questions = sql_questions.scalars().all()
        question_count += len(questions)
        try:
            for question in questions:
                sql_user_answer = await session.execute(select(UserTestAnswer).where(UserTestAnswer.question_id == question.id))
                user_answer = sql_user_answer.scalars().first()
                if user_answer.answer.is_correct:
                    correct += 1
                    
            item = f'Пользователь - <b>{user}</b> тест <b>{test.title}</b> - набранные баллы {correct}/{question_count}'
            users.append(item)
        except Exception as ex:
            print(ex)
    return users