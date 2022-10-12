from aiogram import types
from src.settings.config_bot import STRINGS
from src.settings.telegram_bot import bot
from src.database import database
from src.handlers import states
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData


async def create_ticket(query: types.CallbackQuery):
    await query.message.delete()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["TICKET_CONTACT"].format("tecnico"),callback_data="tecnico"),
        types.InlineKeyboardButton(STRINGS["TICKET_CONTACT"].format("grafico"),callback_data="grafico"),
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start')
    )
    await bot.send_message(query.message.chat.id,STRINGS["CHOOSE_ROLE"],reply_markup=keyboard_markup,parse_mode="html")
    
async def build_ticket(query: types.CallbackQuery,state: FSMContext):
    await query.message.delete()
    await state.update_data(role=query.data)
    await states.Form.description.set()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["MENU"],callback_data="start"),
    )
    await bot.send_message(query.message.chat.id,STRINGS["TICKET_DESCRIPTION"].format(query.data),parse_mode="html",reply_markup=keyboard_markup)
    
    
async def summary_ticket(message: types.Message,state: FSMContext):
    await state.update_data(description=message.text)
    await state.update_data(username=message.from_user.username)
    data = await state.get_data()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["TICKET_SEND"],callback_data="ticket_sent"),
        types.InlineKeyboardButton(STRINGS["MENU"],callback_data='start')
    )
    await bot.send_message(message.chat.id,STRINGS["SUMMARY"].format(data["role"],message.text),reply_markup=keyboard_markup,parse_mode="html")

async def ticket_sent(query: types.CallbackQuery,state: FSMContext):
    await query.message.delete()
    data = await state.get_data()
    
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["MENU"],callback_data="start"),
    )
    await bot.send_message(query.message.chat.id,STRINGS["TICKET_SENT"],parse_mode="html",reply_markup=keyboard_markup)
    ticket_date= database.insert_ticket(query.from_user.id,data["description"],data["role"])
    await forward_ticket(data["description"],data["role"],data["username"],ticket_date)
    await state.finish()

async def forward_ticket(description: str,role: str,username: str,date: str):
    ids = list(set(database.get_ids_by_role(role) + database.get_admins()))
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(STRINGS["CLAIM_TICKET"],callback_data='claim_ticket_{0}'.format(date)),
        types.InlineKeyboardButton(STRINGS["BACK"],callback_data='start')
    )
    for id in ids:
        await bot.send_message(id,STRINGS["NEW_TICKET"].format(role,username,description),parse_mode="html",reply_markup=keyboard_markup)
    