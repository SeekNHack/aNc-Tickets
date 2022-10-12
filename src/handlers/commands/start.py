from aiogram import types
from src.settings.config_bot import STRINGS
from src.settings.telegram_bot import bot
from src.database import database
from src.handlers import states
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData


async def start_user(chat_id,username):
    res=STRINGS["START"].format(username)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["TICKET"],callback_data='create_ticket'),
        types.InlineKeyboardButton(STRINGS["MY_TICKET"],callback_data='my_ticket'),
    )
    await bot.send_message(chat_id,res,parse_mode="html",reply_markup=keyboard_markup)
    

async def start_callback(query: types.CallbackQuery,state: FSMContext) -> None:
    await state.finish()
    await query.message.delete()
    await start(query,state)

async def start_role(chat_id,username ,role: str) -> None:
    res= STRINGS["START_ROLE"].format(username,role)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["TICKET"],callback_data='create_ticket'),
        types.InlineKeyboardButton(STRINGS["ALL_TICKETS"],callback_data='all_tickets'),
        types.InlineKeyboardButton(STRINGS["MY_TICKETS"],callback_data='my_ticket'),
    )
    await bot.send_message(chat_id,res,parse_mode="html",reply_markup=keyboard_markup)

async def start_admin(chat_id,username):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["TICKET"],callback_data='create_ticket'),
        types.InlineKeyboardButton(STRINGS["ALL_TICKETS"],callback_data='all_tickets'),
        types.InlineKeyboardButton(STRINGS["STAFF_OPTIONS"],callback_data='staff_options'),
        types.InlineKeyboardButton(STRINGS["SEE_LOGS"],callback_data='see_logs'),
    )
    await bot.send_message(chat_id,STRINGS["START_ADMIN"].format(username),parse_mode="html",reply_markup=keyboard_markup)

async def start(message: types.Message,state: FSMContext) -> None:
    await state.finish()
    chat_id = message.from_user.id
    username = message.from_user.username
    
    #Se l'utente non è registrato
    if not database.is_registered(chat_id):
        database.add_user(chat_id,username,admin=False)
    #Vedo se l'utente è admin
    if database.is_admin(chat_id):
        #Se è admin gli mando comando start admin
        await start_admin(chat_id,username)
    elif database.has_role(chat_id):
        await start_role(chat_id,username,database.get_role(chat_id))
    else:
        await start_user(chat_id,username)