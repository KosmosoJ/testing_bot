from aiogram.fsm.state import StatesGroup, State


class TestStates(StatesGroup):
    choice = State()
    get_title = State()
    
    get_test = State()
    
    edit_test = State()
    get_test_title = State()
    
    delete_test = State()
    
class QuestionStates(StatesGroup):
    choice = State()
    ask_question_title = State()
    get_question_title = State()
    ask_test = State()
    
    delete_task = State()
    ask_delete_question = State()
    
    ask_test_edit = State()
    get_question_to_edit = State()
    get_new_question = State()
    
    get_tests = State()

class AnswersStates(StatesGroup):
    choice = State()
    get_test = State()
    get_question = State()
    
    A1=State()
    A2=State()
    A3=State()
    A4=State()
    
    task = State()
    
    edit_answer_get_test = State()
    edit_answer_get_answer = State()
    edit_answer_get_new_answer = State()
    edit_answer_process_new_answer = State()
    
    send_answers_get_test = State()
    send_answers = State()