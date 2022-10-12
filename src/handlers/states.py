from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    description= State()

class Role(StatesGroup):
    id= State()
    role=State()