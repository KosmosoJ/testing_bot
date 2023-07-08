from aiogram.fsm.state import StatesGroup, State

class UserStates(StatesGroup):
    choice = State()
    
    select_test = State()
    
    question = State()