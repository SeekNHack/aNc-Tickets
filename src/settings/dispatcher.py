from aiogram import Dispatcher
from aiogram.types import ChatType
from .telegram_bot import bot
from ..handlers.commands import start, tickets,role,staff
from ..handlers import states
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
#Creo il dispatcher
dp = Dispatcher(bot,storage=storage)


#Registro i vari handlers

#Start
dp.register_message_handler(start.start, commands="start", state="*",chat_type=ChatType.PRIVATE)
dp.register_callback_query_handler(start.start_callback,text="start",state="*",chat_type=ChatType.PRIVATE)

#Tickets
dp.register_callback_query_handler(tickets.create_ticket,text='create_ticket')
dp.register_callback_query_handler(tickets.build_ticket,text=['tecnico',"grafico"])
dp.register_message_handler(tickets.summary_ticket,state=states.Form.description)
dp.register_callback_query_handler(tickets.ticket_sent,text='ticket_sent',state=states.Form.description)


#Gestione Tickets
dp.register_callback_query_handler(role.all_tickets,text='all_tickets')
dp.register_callback_query_handler(role.ticket_details,regexp='ticket_details.*')
dp.register_callback_query_handler(role.close_ticket,regexp='close_ticket.*')
dp.register_callback_query_handler(role.claim_ticket,regexp='claim_ticket.*')
dp.register_callback_query_handler(role.clear_logs,text='clear_logs')
dp.register_callback_query_handler(role.ask_clear_logs,text='ask_clear_logs')
dp.register_callback_query_handler(role.see_logs,text='see_logs')

dp.register_callback_query_handler(role.my_tickets,text='my_ticket')


#Gestione staff
dp.register_callback_query_handler(staff.staff_options,text='staff_options')
dp.register_callback_query_handler(staff.assign_role,text='assign_role')
dp.register_callback_query_handler(staff.what_role,text=['ruolo_tecnico','ruolo_grafico',"ruolo_rimosso"],state=states.Role.role)
dp.register_callback_query_handler(staff.staff_list,text='staff_list',state="*")
dp.register_callback_query_handler(staff.staff_detail,regexp='detail_staff.*')
dp.register_callback_query_handler(staff.change_role,text='change_role')
dp.register_message_handler(staff.handle_forward,state=states.Role.id)