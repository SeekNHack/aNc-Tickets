from aiogram import types
from src.settings.config_bot import STRINGS
from src.settings.telegram_bot import bot
from src.database import database
from src.handlers import states
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData



async def staff_options(query: types.CallbackQuery):
    await query.message.delete()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["ASSIGN_ROLE"],callback_data='assign_role'),
        types.InlineKeyboardButton(STRINGS["STAFF_LIST"],callback_data='staff_list'),
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start'),
    )
    await bot.send_message(query.message.chat.id,STRINGS["STAFF_OPTIONS"],reply_markup=keyboard_markup)
    
async def assign_role(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='staff_list'),
    )
    await states.Role.id.set()
    await bot.send_message(query.message.chat.id,STRINGS["FORWARD_MESSAGE"],reply_markup=keyboard_markup)

async def handle_forward(message: types.Message,state: FSMContext):
    id_usr= message.forward_from.id
    username= message.forward_from.username
    await state.update_data(id=id_usr)
    await state.update_data(username=username)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["TECH"],callback_data='ruolo_tecnico'),
        types.InlineKeyboardButton(STRINGS["GRAPHIC"],callback_data='ruolo_grafico'),
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='staff_list'),
    )
    await states.Role.role.set()
    await bot.send_message(message.chat.id,STRINGS["WHAT_ROLE"].format(message.forward_from.username),reply_markup=keyboard_markup)

async def what_role(query: types.CallbackQuery,state: FSMContext):
    await query.message.delete()
    data = await state.get_data()
    id= data['id']
    username= data['username']
    role = query.data.split('_')[1]
    role = "" if role == "rimosso" else role
    message = STRINGS["ROLE_REMOVED"].format(username) if role == "" else STRINGS["ROLE_ASSIGNED"].format(username,role)
    #Check se l'utente è registrato
    if not database.is_registered(id):
        database.add_user(id,username,False)
    database.set_role(id,role)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='staff_list'),
    )
    await bot.send_message(query.message.chat.id,message,reply_markup=keyboard_markup)
    await state.finish()
    
async def staff_list(query: types.CallbackQuery,state: FSMContext):
    await query.message.delete()
    await state.finish()
    #Prendo la lista degli utenti che hanno un ruolo
    users = database.get_all_users_with_role()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    for user in users:
        username= database.get_username(user)
        keyboard_markup.add(
            types.InlineKeyboardButton(STRINGS["STAFF_MEMBER"].format(username,database.get_role(user)),callback_data='detail_staff_{}'.format(user)),
        )
    keyboard_markup.add(
            types.InlineKeyboardButton(STRINGS["BACK"],callback_data='staff_list'),
    )
    await bot.send_message(query.message.chat.id,STRINGS["DETAIL_STAFF"],reply_markup=keyboard_markup)
    
async def staff_detail(query: types.CallbackQuery,state: FSMContext):
    await query.message.delete()
    id_usr=int(query.data.split('_')[2])
    await state.update_data(id=id_usr)
    ticket_assigned = len(database.get_tickets_by_user(id_usr))
    ticket_closed = len(database.get_closed_tickets_by_user(id_usr))
    await state.update_data(username=database.get_username(id_usr))
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["CHANGE_ROLE"],callback_data='change_role'),
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start'),
    )
    await bot.send_message(query.message.chat.id,STRINGS["STAFF_DETAILS"].format(database.get_username(id_usr),database.get_role(id_usr),id_usr,ticket_assigned,ticket_closed),reply_markup=keyboard_markup)


async def change_role(query: types.CallbackQuery,state: FSMContext):
    await query.message.delete()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["TECH"],callback_data='ruolo_tecnico'),
        types.InlineKeyboardButton(STRINGS["GRAPHIC"],callback_data='ruolo_grafico'),
        types.InlineKeyboardButton(STRINGS["REMOVE_ROLE"],callback_data='ruolo_rimosso'),
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='staff_list'),
    )
    data = await state.get_data()
    username = data['username']
    await states.Role.role.set()
    await bot.send_message(query.message.chat.id,STRINGS["WHAT_ROLE"].format(username),reply_markup=keyboard_markup)
