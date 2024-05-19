from inventory import Inventory
from database import DB
from item import Item_methods
from notifications import Notifications
from stn import Stn

from requests import codes
from time import sleep
from sys import exit
import sqlite3
from time import time
import configparser
#TODO: implement proper logging
import logging

# config
config = configparser.ConfigParser()
config.read('data/config.ini')
# init variables from config
log_file_path = config.get("Paths", "log")
database_file_path = config.get("Paths", "database")
# Table
all_items_table = config.get("Table", "items")
new_items_table = config.get("Table", "new_items")
valuable_items_table = config.get("Table", "valuable_items")
error_table = config.get("Table", "error")
bots_table = config.get("Table", "bots")
stn_table = config.get("Table", "stn")
# Valuable
valuable_sheens = config.get("Valuable", "sheens")
valuable_killstreakers = config.get("Valuable", "killstreakers")
valuable_parts = config.get("Valuable", "parts")
valuable_paints = config.get("Valuable", "paints")
# Aspects
parts = config.get("Aspects", "parts")
# STN
stn_api_key = config.get("STN", "api_key")

# logger
print(log_file_path)
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)
logger.info(f"{int(time())} Program started")

# creates sqlite3 connection, cursor and loads DB class
connect = sqlite3.connect(database=database_file_path)
cursor = connect.cursor()
database = DB(conn=connect)
# loads rest of classes
inventory = Inventory(parts = parts, valuable_parts = valuable_parts, valuable_paints = valuable_paints, 
                    valuable_sheens = valuable_sheens, valuable_killstreakers = valuable_killstreakers)
item = Item_methods(parts = parts, valuable_parts = valuable_parts, valuable_paints = valuable_paints, 
                    valuable_sheens = valuable_sheens, valuable_killstreakers = valuable_killstreakers)
notifications = Notifications(token = "7106357963:AAGVHfEj4kzhF5am444SIfpB8kRttDy_FHI", chat_id = "6653108996")
stn = Stn(connect=connect, table=stn_table, api_key=stn_api_key)

def add_run(*, success: int, reason: str, time: int = int(time())):
    cursor.execute(f"INSERT INTO {error_table} VALUES (?, ?, ?);", (success, reason, time))

# HERE IS WHERE THE ACTUAL CODE STARTS

# which categories of bots to perse sorry :(
categories = ["killstreaks"]
# gets steamids from database by categories
#steamids = database.get_steamids_from_categories("stn_bots", categories)
steamids = database.get_all_steamids("stn_bots")
steamids = steamids[5:6]
#steamids = database.get_all_steamids("scraptf_bots")
#steamids = steamids[17:]

# deletes all previously loaded new items
database.delete_all_from_column(new_items_table)

all_valuable_items = []
tries = 0
for steamid in steamids:
    # gets inv
    inv, status = inventory.fetch_inventory(steam_id=steamid)
    
    if status == codes.ok:
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

    elif status == codes.too_many_requests:
        tries += 1
        print("could not load steamid inventory", steamid)
        print(status, "sleeping for 30 seconds")
        sleep(30)
    elif status == codes.internal_server_error:
        print(status, "internal server error")
        print("exiting...")
        exit(1)
    else:
        tries += 1
        print("could not load steamid inventory", steamid)

    # if tries exceed 2 close program and report error
    if tries > 2:
        logger.info(f"{int(time())} Ran unsuccessfully, tried too many times")
        add_run(success=0, reason="Ran unsuccessfully, tried too many times", time=int(time()))
        print(f"tried {tries} times, exiting...")
        exit(1)

print(all_valuable_items)
# creates telegram message
if all_valuable_items:
    add_run(success=1, reason=f"Ran successfully, found {len(all_valuable_items)} valuable items", time=int(time()))

    message = f"{len(all_valuable_items)} valuable items"
    for item in all_valuable_items:
        name = None
        try:
            name = cursor.execute("SELECT name FROM stn_bots WHERE steamid = ?;", (item.steamid, )).fetchone()[0]
        except Exception:
            pass
        
        stn_item = stn.search(item.name)
        link = None
        if stn_item:
            link = stn.create_item_link(stn_item["name"])

        if name and link:
            message += f"\nNAME: {item.name}, BOT: {name}, LINK: {link}\n"
        elif name:
            message += f"\nNAME: {item.name}, BOT: {name}\n"
        else:
            message += f"\nNAME: {item.name}\n"

    # sends telegram message
    notifications.send_message(message = message)
else:   
    add_run(success=1, reason=f"Ran successfully, found no valuable items", time=int(time()))

#commits all changes to database
database.connect.commit()