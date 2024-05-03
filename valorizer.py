from inventory import Map_inventory, Load_inventory
from database import DB
from item import Item_methods
from notifications import Notifications
from data.config import config
#TODO: implement logging
import logging

from requests import codes
from time import sleep
from sys import exit
import sqlite3
from time import time

# configures a logger
logging.basicConfig(filename=config["log_file_path"], level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)
logger.info(f"{int(time())} Program started")

# creates sqlite3 connection, cursor and loads DB class
connect = sqlite3.connect(config["database_file_path"])
cursor = connect.cursor()
database = DB(connect)
# loads rest of classes
Loader = Load_inventory()
Mapper = Map_inventory()
item = Item_methods()
notifications = Notifications(token = "7106357963:AAGVHfEj4kzhF5am444SIfpB8kRttDy_FHI", chat_id = "6653108996")

# gets tables
item_table = config["tables"]["item_table"]
new_item_table = config["tables"]["new_item_table"]
valuable_item_table = config["tables"]["valuable_item_table"]
error_table = config['tables']['error_table']

def add_run(*, success: int, reason: str, time: int = int(time())):
    cursor.execute(f"INSERT INTO {error_table} VALUES (?, ?, ?);", (success, reason, time))

# which categories of bots to perse sorry :(
categories = ["vintages"]
# gets steamids from database by categories
steamids = database.get_steamids_from_categories("stn_bots", categories)
#steamids = database.get_all_steamids("stn_bots")

# deletes all previously loaded new items
database.delete_all_from_column(new_item_table)

all_valuable_items = []
tries = 0
for steamid in steamids:
    # gets inv
    inv, status = Loader.fetch_inventory(steamid)
    
    if status == codes.ok:
        tries = 0

        # maps item instances with their descriptions and gets inv as dict from json 
        inv = Mapper.map_inventory(inv, steamid)

        # compares inv to last and picks out new items
        new_items = database.compare_items(inv, item_table)

        # adds ONLY new items to database
        database.add_items(new_items, new_item_table)

        # deletes old items from item column
        database.delete_from_column_where_steamid(item_table, steamid)

        # adds all items to database
        database.add_items(inv, item_table)

        # checks for valuable items
        valuable_items = item.find_valuable_items(items=new_items)

        # adds valuable items to database
        database.add_items(valuable_items, valuable_item_table)

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
        message += "\n" + item.name

    # sends telegram message
    notifications.send_message(message = message)
else:
    add_run(success=1, reason=f"Ran successfully, found no valuable items", time=int(time()))

#commits all changes to database
database.connect.commit()