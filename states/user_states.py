from aiogram.fsm.state import State, StatesGroup

class AskExpertState(StatesGroup):
    choosing_system = State()
    choosing_phase = State()
    writing_question = State()

class SubscriptionState(StatesGroup):
    confirming = State()

class B2BState(StatesGroup):
    waiting_company = State()
    waiting_email = State()
    