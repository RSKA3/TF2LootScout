from get_inventory import LoadInventory
from inventory import MatchInventory
from schema import Schema
from database import DB
from item import Item
from notifications import Notifications

from requests import codes
from time import sleep
from sys import exit
import requests
import time

Loader = LoadInventory()
Matcher = MatchInventory()
database = DB("/home/rasmus/Documents/projects/tf2_bot/scripts/data/items.db")
item = Item()
notifications = Notifications(token = "7106357963:AAGVHfEj4kzhF5am444SIfpB8kRttDy_FHI", chat_id = "6653108996")

# bots : https://stntrading.eu/about-us

# name of databases
item_database = "stn_bot_items"
new_item_database = "new_stn_bot_items"
valuable_item_database = "valuable_stn_bot_items"
# which categories of bots to perse sorry :(
categories = ["hats"]
# gets steamids from database by categories
#steamids = database.get_steamids_from_categories("stn_bots", categories)
steamids = database.get_all_steamids("stn_bots")


# deletes all "new" items
database.delete_all_from_column(new_item_database)

all_valuable_items = []
tries = 0
for steamid in steamids:
    # gets inv
    inv, status = Loader.fetch_inventory(steamid)

    if inv:
        tries = 0

        # gets inv as dict from json 
        inv = Matcher.map_inventory(inv, steamid)

        # compares inv to last and picks out new items
        new_items = database.compare_items(inv, item_database)

        # adds ONLY new items to database
        database.add_items(new_items, new_item_database)

        # deletes old items from item column
        database.delete_from_column_where_steamid(item_database, steamid)

        # adds all items to database
        database.add_items(inv, item_database)

        # checks for valuable items
        valuable_items = item.find_valuable_items(new_items)

        # adds valuable items to database
        database.add_items(valuable_items, valuable_item_database)

        all_valuable_items.extend(valuable_items)

        #sleep(10)

    elif status == codes.too_many_requests:
        tries += 1
        print("could not load steamid inventory", steamid)
        print(status, "sleeping for 30 seconds")
        sleep(30)
    else:
        tries += 1
        print("could not load steamid inventory", steamid)

    if tries > 2:
        print(f"tried {tries} times, exiting...")
        exit(1)

database.commit()

# creates telegram message
message = f"{len(all_valuable_items)} valuable items"
for item in all_valuable_items:
    message += "\n" + item["name"]
# sends telegram message
notifications.send_message(message = message)