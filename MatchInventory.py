from item import Item

class MatchInventory():
    def __init__(self):
        self.item = Item()

    def map_inventory(self, inventory, steamid = None) -> list:
        # create list of items
        items = []
        for asset in inventory["assets"]:
            for description in inventory["descriptions"]:
                if asset["classid"] == description["classid"] and asset["instanceid"] == description["instanceid"]:
                    item = self.item.to_item(asset, description, steamid)
                    items.append(item)
        return items
        
        # create item object with all the values
            # Item = {
                # "name" : "etc"
                # "inventory" : "etc" }
            # classId, instanceId, assetId, tradeable, name, quality, type, class, rarity, collection, exterior
            # create item sku from item object and add it to item object
        # return item