from tinydb import TinyDB, Query
from datetime import datetime
#Carico il database
DB = TinyDB('./src/database/db.json')

TICKETS = TinyDB('./src/database/tickets.json')
CLOSED_TICKETS= TinyDB('./src/database/closed_tickets.json')

def add_user(id,username,admin):
    if not is_admin(id):
        DB.insert({'id': id, 'username': username,'admin': admin, "role": "","open_tickets": 0})

def is_registered(id):
    return DB.contains(Query().id == id)

def is_admin(id):
    return DB.contains((Query().id == id) & (Query().admin == True))

def remove_user(id):
    DB.remove(Query().id == id)

def set_role(id, role):
    DB.update({'role': role}, Query().id == id)
    return True
    
def insert_ticket(id, description,role):
    date= datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    TICKETS.insert({'user_id': id, 'description': description,"assigned": "","role": role,"date": date,"closed_by": "", "closed_date": ""})
    return date

def claim_ticket(id,date):
    #Check se il ticket è già stato preso
    if TICKETS.search(Query().date == date)[0]['assigned'] == "":
        TICKETS.update({'assigned': id}, Query().date == date)
        return True
    return False
    
def close_ticket(date,closer):
    #Rimuovo il ticket
    TICKETS.update({'status': 'closed', 'closed_by': closer, 'closed_date': datetime.now().strftime("%d/%m/%Y %H:%M:%S")}, Query().date == date)
    ticket = TICKETS.search(Query().date == date)[0]
    TICKETS.remove(Query().date == date)
    CLOSED_TICKETS.insert(ticket)
    
def get_ids_by_role(role):
    #Restituisco una lista di id di utenti con un ruolo specifico
    return [user['id'] for user in DB.search(Query().role == role)]

def get_tickets_by_role(role):
    #Restituisco una lista di ticket con un ruolo specifico
    return TICKETS.search(Query().role == role)
def get_ticket_by_date(date):
    return TICKETS.search(Query().date == date)[0]
def get_role(id):
    res= DB.search(Query().id == id)[0]['role']
    return res
def has_role(id):
    return DB.search(Query().id == id)[0]['role'] != ""
def get_username(id):
    res = DB.search(Query().id == id)
    if len(res)==0:
        return ""
    return res[0]['username']
def get_admins():
    return [user['id'] for user in DB.search(Query().admin == True)]
def get_all_tickets():
    return TICKETS.all()

def get_logs():
    return CLOSED_TICKETS.all()

def clear_logs():
    all = CLOSED_TICKETS.all()
    for ticket in all:
        CLOSED_TICKETS.remove(Query().date == ticket['date'])
        
def get_all_users_with_role():
   return [user['id'] for user in DB.search((Query().role != "") & (Query().admin == False))]


#Prendi tutti i ticket assegnati a un utente
def get_tickets_by_user(id):
    return [ticket for ticket in TICKETS.all() if ticket['assigned'] == id]

#Prendi tutti i ticket chiusi da un utente
def get_closed_tickets_by_user(id):
    return [ticket for ticket in CLOSED_TICKETS.all() if ticket['closed_by'] == id] 

def is_dev(id):
    return DB.search(Query().id == id)[0]['role'] == "dev"