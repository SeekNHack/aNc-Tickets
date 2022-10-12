from aiogram import types
from src.settings.config_bot import STRINGS
from src.settings.telegram_bot import bot
from src.database import database
from src.handlers import states
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData


async def all_tickets(query: types.CallbackQuery,state: FSMContext):
    await query.message.delete()
    tickets = database.get_tickets_by_role(database.get_role(query.from_user.id))
    if database.is_admin(query.from_user.id):
        tickets = database.get_all_tickets()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    if(len(tickets)==0):
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start'),
        )
        await bot.send_message(query.message.chat.id,STRINGS["NO_TICKETS"],reply_markup=keyboard_markup)
    else:
        for ticket in tickets:
            username = database.get_username(ticket["user_id"])
            data = ticket["date"]
            assigned = "-" if ticket["assigned"]=="" else ticket["assigned"]
            claimed_by=  database.get_username(assigned) if assigned!="-" else "-"
            keyboard_markup.add(
                types.InlineKeyboardButton(STRINGS["TICKET_LIST"].format(username,claimed_by),callback_data='ticket_details_{0}'.format(data))
            )
        keyboard_markup.add(
            types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start'),
        )
        await bot.send_message(query.message.chat.id,STRINGS["ALL_TICKETS"],reply_markup=keyboard_markup)
        
async def ticket_details(query: types.CallbackQuery):
    await query.message.delete()
    ticket_date = query.data.split("_")[2]
    ticket = database.get_ticket_by_date(ticket_date)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)

    if ticket["assigned"] == "":
        keyboard_markup.add(
            types.InlineKeyboardButton(STRINGS["CLAIM_TICKET"],callback_data='claim_ticket_{0}'.format(ticket["date"])),
        )
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["CLOSE_TICKET"],callback_data='close_ticket_{0}'.format(ticket["date"])),
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='all_tickets'),
    )
    await bot.send_message(query.message.chat.id,STRINGS["TICKET_DETAILS"].format(database.get_username(ticket["user_id"]),ticket["description"],ticket["date"]),reply_markup=keyboard_markup,parse_mode="html")
    
async def close_ticket(query: types.CallbackQuery):
    await query.message.delete()
    ticket_date = query.data.split("_")[2]
    ticket= database.get_ticket_by_date(ticket_date)
    database.close_ticket(ticket_date,query.from_user.id)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["ALL_TICKETS"],callback_data='all_tickets'),
    )
    await bot.send_message(query.message.chat.id,STRINGS["TICKET_CLOSED"],reply_markup=keyboard_markup,parse_mode="html")
    await bot.send_message(ticket["user_id"],STRINGS["TICKET_CLOSED_USER"].format(ticket["role"],ticket_date,query.from_user.username,ticket["description"]),parse_mode="html")

async def claim_ticket(query: types.CallbackQuery):
    await query.message.delete()
    ticket_date = query.data.split("_")[2]
    ticket= database.get_ticket_by_date(ticket_date)
    res = database.claim_ticket(query.from_user.id,ticket_date)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
            types.InlineKeyboardButton(STRINGS["ALL_TICKETS"],callback_data='all_tickets'),
    )
    if res:
        #Mando il messaggio al tecnico
        await bot.send_message(query.message.chat.id,STRINGS["TICKET_CLAIMED"],reply_markup=keyboard_markup,parse_mode="html")
        #Mando il messaggio all'utente
        await bot.send_message(ticket["user_id"],STRINGS["TICKET_CLAIMED_USER"].format(ticket["role"],query.from_user.username),parse_mode="html")
        #Notifico gli admin
        await notify_admin(STRINGS["TICKET_CLAIMED_ADMIN"].format(ticket["role"],ticket["user_id"],ticket_date,query.from_user.username))
    else:
        #Mando il messaggio al tecnico di errore
        await bot.send_message(query.message.chat.id,STRINGS["TICKET_CLAIMED_USER"].format(query.from_user.username),reply_markup=keyboard_markup,parse_mode="html")
        
        
async def notify_admin(message):
    admins = database.get_admins()
    for admin in admins:
        await bot.send_message(admin["user_id"],message,parse_mode="html")
        
        
async def see_logs(query: types.CallbackQuery):
    await query.message.delete()
    await bot.send_message(query.message.chat.id,STRINGS["LOGS_START"],parse_mode="html")
    logs = database.get_logs()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    if len(logs)!=0:
        keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["CLEAR_LOGS"],callback_data='ask_clear_logs'),
    )
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start'),
    )
    for log in logs:
        opener = database.get_username(log["user_id"])
        closer = database.get_username(log["closed_by"])
        data_opened = log["date"]
        description = log["description"]
        data_closed = log["closed_date"]
        claimed_by = database.get_username(log["assigned"])
        await bot.send_message(query.message.chat.id,STRINGS["LOGS"].format(opener,data_opened,claimed_by,description,closer,data_closed),parse_mode="html")
    await bot.send_message(query.message.chat.id,STRINGS["LOGS_END"],reply_markup=keyboard_markup,parse_mode="html")
    
async def ask_clear_logs(query: types.CallbackQuery):
    await query.message.delete()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["CLEAR_LOGS"],callback_data='clear_logs'),
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start')
    )
    await bot.send_message(query.message.chat.id,STRINGS["ASK_CLEAR_LOGS"],parse_mode="html",reply_markup=keyboard_markup)

async def clear_logs(query: types.CallbackQuery):
    await query.message.delete()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start')
    )
    database.clear_logs()
    await bot.send_message(query.message.chat.id,STRINGS["CLEARED_LOGS"],parse_mode="html",reply_markup=keyboard_markup)
    
    
async def my_tickets(query: types.CallbackQuery):
    await query.message.delete()
    tickets = database.get_tickets_by_user(query.from_user.id)
    print(tickets)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    for ticket in tickets:
        data = ticket["date"]
        role = ticket["role"]
        assigned = "-" if ticket["assigned"]=="" else ticket["assigned"]
        claimed_by=  database.get_username(assigned) if assigned!="-" else "-"
        keyboard_markup.add(
            types.InlineKeyboardButton(STRINGS["TICKET_LIST_USER"].format(role,claimed_by),callback_data='ticket_details_{0}'.format(data))
            )
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start'),
    )
    await bot.send_message(query.message.chat.id,STRINGS["MY_TICKETS_END"],parse_mode="html",reply_markup=keyboard_markup)
    