import requests
import json

from item import Item_methods

class Load_inventory():
    def __init__(self):
        self.session = requests.Session()

    def fetch_inventory(self, steam_id: str):
        Url = self.get_inventory_url(steam_id)
        Inventory = self.session.get(Url)
        print(Inventory.url, "status code: " + str(Inventory.status_code))

        try:
            return [Inventory.json(), Inventory.status_code]
        except:
            return [False, Inventory.status_code]
        
    def save_inventory_to_file(self, inventory: dict, filename: str = "data/inventory.json"):
        with open(filename, "w") as InventoryFile:
            json.dump(inventory, InventoryFile)

    def load_inventory_from_file(self, filename = "data/inventory.json"):
        with open(filename) as InventoryFile:
            return json.load(InventoryFile)
        
    def get_inventory_url(self, steam_id: str, gameId = 440, contextId = 2, count: int = 3000):
        return f"https://steamcommunity.com/inventory/{steam_id}/{gameId}/{contextId}?count={count}"

#steamcommunity.com/profiles/steamid/inventory#appid_contextid_assetid


class Map_inventory():
    def __init__(self):
        self.item = Item_methods()

    def map_inventory(self, inventory, steamid = None) -> list:
        # create list of items
        items = []
        for asset in inventory["assets"]:
            for description in inventory["descriptions"]:
                if asset["classid"] == description["classid"] and asset["instanceid"] == description["instanceid"]:
                    item = self.item.to_item(asset=asset, description=description, steamid=steamid)
                    
                    items.append(item)
        return items
        
        # create item object with all the values
            # Item = {
                # "name" : "etc"
                # "inventory" : "etc" }
            # classId, instanceId, assetId, tradeable, name, quality, type, class, rarity, collection, exterior
            # create item sku from item object and add it to item object
        # return item