from GetInventory import LoadInventory
from MatchInventory import MatchInventory
from schema import Schema
from database import DB
from requests import codes
from time import sleep
from sys import exit

Loader = LoadInventory()
Matcher = MatchInventory()
database = DB("/home/rasmus/Documents/projects/tf2_bot/scripts/data/items.db")

#steamids_killstreaks = ["76561198383794129", "76561199582352552"]
#steamids_hats = ["76561198310024994", "76561198309998421", "76561198310454087", "76561198309976634", "76561198310524424", 
#                 "76561199582907694", "76561198309190452", "76561198309291300", "76561198309405764", "76561198923568511"]
#steamids_stranges = ["76561198310691078", "76561198309750232"]
#steamids_vintages = ["76561198310188284"]
#steamids_weapons = ["76561198311319887"]
#steamids_skins = ["76561198311521627", "76561199026476781"]
#steamids_genuines = ["76561198309246958"]

#with open("/home/rasmus/Documents/projects/tf2_bot/scripts/data/bots.csv", "r") as file:
#    bots = [line.rstrip() for line in file]
#    bots = bots[434:]

steamids = database.get_all_steamids("stn_bots")

tries = 0
for steamid in steamids:
    inv, status = Loader.fetch_inventory(steamid)

    if inv:
        tries = 0
        inv = Matcher.map_inventory(inv, steamid)
        new_items = database.compare_items(inv, "stn_bot_items")
        database.add_items(new_items, "new_stn_bot_items")
        database.add_items(inv, "stn_bot_items")
        #valuable_items = database.find_valuable_items_database("new_stn_bot_items")
        #database.add_items(valuable_items, "valuable_new_stn_strange_bots")
        sleep(10)
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