import requests
import json

class LoadInventory():
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


