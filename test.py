from database import DB
from item import Item

database = DB("/home/rasmus/Documents/projects/tf2_bot/scripts/data/items.db")
#item = {"steamid" : "0", "assetid" : "0", "classid" : "0", "instanceid" : "0"}
item = {'steamid': '76561198311521627', 'assetid': '13837244037', 'classid': '2798763239', 'instanceid': '4672250409', 'tradable': 1, 'craftable': 1, 'name': 'Strange Cardboard Boxed SMG (Battle Scarred)', 'quality': 'strange', 'type': 'secondary', 'rarity': None, 'collection': None, 'exterior': 'TFUI_InvTooltip_BattleScared', 'sku': None, 'killstreaks': None, 'sheen': None, 'killstreaker': None, 'paint': '    Bloom Buffed War Paint', 'spell': None, 'effect': None, 'parts': '     Kills'}

print(Item().find_valuable_items([item]))