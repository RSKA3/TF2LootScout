from inventory import Inventory
from database import DB
from item import Item_methods
from notifications import Notifications
from stn import Stn
from logger import setup_logger, clear_log_file, is_week_since_last_clear, store_last_cleared_date

from requests import codes
from time import sleep
from sys import exit
import sqlite3
import configparser
import os

# gets path from env variable
env = 'VALORIZER_APP_PATH'
app_path = os.getenv(env)
if app_path is None:
    raise ValueError(f"Environment variable {env} is not set")
print(f"App path is: {app_path}")

# config
config_file_path = app_path+"data/config.ini"
config = configparser.ConfigParser()
config.read(config_file_path)
# init variables from config
# Path
app_data_path = app_path + config.get("Paths", "app_data")
log_file_path = app_data_path + config.get("Paths", "log")
database_file_path = app_data_path + config.get("Paths", "database")
# Table
all_items_table = config.get("Table", "items")
new_items_table = config.get("Table", "new_items")
valuable_items_table = config.get("Table", "valuable_items")
bots_table = config.get("Table", "bots")
stn_table = config.get("Table", "stn")
# Valuable
valuable_sheens = [sheen.strip() for sheen in config.get("Valuable", "sheens").split(",")]
valuable_killstreakers = [killstreaker.strip() for killstreaker in config.get("Valuable", "killstreakers").split(',')]
valuable_parts = [part.strip() for part in config.get("Valuable", "parts").split(',')]
valuable_paints = [paint.strip() for paint in config.get("Valuable", "paints").split(',')]
# Aspects
parts = [part.strip() for part in config.get("Aspects", "parts").split(",")]
# STN
stn_api_key = config.get("STN", "api_key")
# telegram
telegram_message_max_length = config.getint("Telegram", "message_max_length")
telegram_token = config.get("Telegram", "token")
telegram_chat_id = config.get("Telegram", "chat_id")

# set up logging
logger = setup_logger(name = "Valorizer", log_file=log_file_path)
logger.log(level=20, msg = f"logger setup, started running")

# clears logger if its been 7 days since last clear
if is_week_since_last_clear(config_file=config_file_path):
    clear_log_file(log_file_path)
    store_last_cleared_date(config_file=config_file_path)

# creates sqlite3 connection, cursor and loads DB class
connect = sqlite3.connect(database=database_file_path)
cursor = connect.cursor()

# load classes
database = DB(conn=connect, log_file_path=log_file_path)
inventory = Inventory(parts = parts, valuable_parts = valuable_parts, valuable_paints = valuable_paints, 
                    valuable_sheens = valuable_sheens, valuable_killstreakers = valuable_killstreakers)
item = Item_methods(parts = parts, valuable_parts = valuable_parts, valuable_paints = valuable_paints, 
                    valuable_sheens = valuable_sheens, valuable_killstreakers = valuable_killstreakers)
notifications = Notifications(token = telegram_token, chat_id = telegram_chat_id)
stn = Stn(connect=connect, table=stn_table, api_key=stn_api_key)

# HERE IS WHERE THE ACTUAL CODE STARTS

# which categories of bots to perse sorry :(
categories = ["killstreaks"]
# gets steamids from database by categories
#steamids = database.get_steamids_from_categories("stn_bots", categories)
steamids = database.get_all_steamids("stn_bots")
#steamids = ["76561198309750232"]

# deletes all previously loaded new items
database.delete_all_from_column(new_items_table)

all_valuable_items = []
tries = 0
for steamid in steamids:
    # gets inv
    inv, status = inventory.fetch_inventory(steam_id=steamid)

    # if tries exceed 2 close program and report error
    if tries > 2:
        logger.log(level=40, msg = f"tried {tries} times to fetch inventory: {status}, exiting...")
        exit(1)

    # handles bad status codes
    if status != codes.ok:
        if status == codes.too_many_requests:
            tries += 1
            logger.log(level=30, msg = f"couldn't load steamid inventory: {status}, sleeping for 30s")
            sleep(30)
        elif status == codes.internal_server_error:
            logger.log(level=30, msg = f"internal server error: {status}, exiting...")
            exit(1)
        else:
            tries += 1
            logger.log(level=30, msg = f"could not load steamid: {steamid} inventory: {status}")
        continue

    logger.log(level=20, msg = f"succesfully fetched: {steamid} inventory: {status}")
    tries = 0

    # maps item instances with their descriptions and gets inv as dict from json 
    inv = inventory.map_inventory(inv, steamid)

    # compares inv to last and picks out new items
    new_items = database.compare_items(inv, all_items_table)
    # adds ONLY new items to database
    database.add_items(new_items, new_items_table)

    # deletes old items from item column
    database.delete_from_column_where_steamid(all_items_table, steamid)
    # adds all items to database
    database.add_items(inv, all_items_table)

    # checks for valuable items
    valuable_items = item.find_valuable_items(items=new_items)
    # adds valuable items to database
    database.add_items(valuable_items, valuable_items_table)
    
    all_valuable_items.extend(valuable_items)
    #sleep(10)

logger.log(level=20, msg = f"successfully ran through all steamids, found {len(all_valuable_items)} valuable items")

print(all_valuable_items)
# creates telegram message
if all_valuable_items:
    # create messages list with first line as messages
    messages = [f"{len(all_valuable_items)} valuable items"]
    for item in all_valuable_items:
        message = f"\nNAME: {item.name}"

        bot_name = cursor.execute("SELECT name FROM stn_bots WHERE steamid = ?;", (item.steamid, )).fetchone()
        if bot_name:
            bot_name = bot_name[0]
        
        stn_item = stn.search(item.name)
        link = None
        if stn_item:
            link = stn.create_item_link(stn_item["name"])

        if bot_name:
            message = f"{message}, BOT: {bot_name}"
        if link:
            message = f"{message}, LINK: {link}"
        message = f"{message}\n"

        messages.append(message)

    # sends telegram message
    notifications.send_messages(messages = messages, max_length=telegram_message_max_length)

#commits all changes to database
database.connect.commit()