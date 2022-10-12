import os
import json
from configparser import ConfigParser


path = "./src/settings/"


# File di configurazione iniziale
config = ConfigParser()
config.read(path+"config.ini")

#Load configs
TOKEN = config.get("bot","token")
#LANG
STRINGS = json.load(open(path+"it.json", encoding='utf-8'))

