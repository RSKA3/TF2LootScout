import requests
import json

from item import Item_methods

class Inventory():
    def __init__(self, *, parts: list, valuable_parts: list, valuable_paints: list, valuable_sheens: list, valuable_killstreakers: list):
        self.item = Item_methods(parts = parts, valuable_parts = valuable_parts, valuable_paints = valuable_paints, 
                                valuable_sheens = valuable_sheens, valuable_killstreakers = valuable_killstreakers)
        self.session = requests.Session()

    def get_inventory_url(self, steam_id: str, gameId = 440, contextId = 2, count: int = 3000):
        return f"https://steamcommunity.com/inventory/{steam_id}/{gameId}/{contextId}?count={count}"

    def fetch_inventory(self, steam_id: str):
        Url = self.get_inventory_url(steam_id)
        Inventory = self.session.get(Url)
        print(Inventory.url, "status code: " + str(Inventory.status_code))

        try:
            return [Inventory.json(), Inventory.status_code]
        except:
            return [False, Inventory.status_code]
        
    def map_inventory(self, inventory, steamid = None, name = None) -> list:
        # create list of items
        items = []
        for asset in inventory["assets"]:
            for description in inventory["descriptions"]:
                if asset["classid"] == description["classid"] and asset["instanceid"] == description["instanceid"]:
                    item = self.item.to_item(asset=asset, description=description, steamid=steamid, bot_name=name)
                    items.append(item)
        return items
        
    # unusued functions, might be useful for debugging
    def save_inventory_to_file(self, inventory: dict, filename: str = "data/inventory.json"):
        with open(filename, "w") as InventoryFile:
            json.dump(inventory, InventoryFile)

    def load_inventory_from_file(self, filename = "data/inventory.json"):
        with open(filename) as InventoryFile:
            return json.load(InventoryFile)

#steamcommunity.com/profiles/steamid/inventory#appid_contextid_assetid