from dataclasses import dataclass
from data.config import config

import re

# TODO: change the projects "getters" to use regex instead

@dataclass
class Item:
    steamid : str = None
    classid : str = None
    instanceid : str = None
    assetid : str = None
    tradable : str = None
    craftable : str = None
    name : str = None
    quality : str = None
    type : str = None
    rarity : str = None
    collection : str = None
    exterior : str = None
    sku : str = None
    killstreaks : str = None
    sheen : str = None
    killstreaker : str = None
    paint : str = None
    spell : str = None
    effect : str = None
    parts : str = None

class Item_methods():
    def __init__(self):
        self.valuable_parts = [part.lower() for part in config["valuable_aspects"]["valuable_parts"]]
        self.valuable_paints = [paint.lower() for paint in config["valuable_aspects"]["valuable_paints"]]
        self.valuable_sheens = [sheen.lower() for sheen in config["valuable_aspects"]["valuable_sheens"]]
        self.valuabale_killstreakers = [killstreaker.lower() for killstreaker in config["valuable_aspects"]["valuable_sheens"]]

        self.parts = [part.lower() for part in config["aspects"]["parts"]]

    #important methods
    def to_item(self, *, asset: dict, description: dict, steamid: str = None) -> dataclass:
        """ Turns asset, description and steamid to a single item dataclass

            Args:
                asset = {'amount': '1', 'appid': 440, 'assetid': '8665095877', 'classid': '331369', 'contextid': '2', 'instanceid': '3773026402'}...
                description = {'appid': 440, 'background_color': '3C352E', 'classid': '331369', 'commodity': 0, 'currency': 0}
                steam_id = '76561199026476781''
            
            Returns:
                instance of dataclass Item
        """

        item = Item()

        # fill in self.item
        item.assetid = asset["assetid"]
        item.steamid = steamid
        item.classid = description["classid"]
        item.instanceid = description["instanceid"]
        item.tradable = description["tradable"]
        item.name = description["market_name"].lower()
        
        # gets quality from tag values
        for tag in description["tags"]:
            if tag["category"].lower() == "quality":
                item.quality = tag["internal_name"].lower()
            elif tag["category"].lower() == "type":
                item.type = tag["internal_name"].lower()

        # gets all description values
        if "descriptions" in description:
            for description in description["descriptions"]:
                self.get_description(description, item)

        return item
    
    def find_valuable_items(self, *, items: list) -> list:
        """ takes in list of Item dataclass and returns list of the valuable items
        
        Args:
            items = [Item, Item, Item]
            
        Returns:
            valuable_items = [Item, Item, Item]
        """
        
        valuabale_items = []
        for item in items:
            if item.paint and item.paint.lower() in self.valuable_paints:
                valuabale_items.append(item)
            elif item.sheen and item.killstreaker and item.killstreaker.lower() in self.valuabale_killstreakers and item.sheen.lower() in self.valuable_sheens:
                valuabale_items.append(item)
            elif item.spell:
                valuabale_items.append(item)
            elif item.parts and any(part.lower() in item.parts.lower() for part in self.valuable_parts):
                valuabale_items.append(item)
        return valuabale_items
            
    def get_description(self, description, item):
        
        value = description["value"].lower()

        if "crafted by" not in value:
            if self.check_sheen_and_killstreaker(value):
                streaker = self.get_sheen_and_killstreaker(value)
                item.sheen = streaker["sheen"]
                item.killstreaker = streaker["killstreaker"]
                item.killstreaks = True

            elif self.check_sheen(value):
                item.sheen = self.get_sheen(value)
                item.killstreaks = True

            elif self.check_killstreaker(value):
                item.killstreaks = True

            elif self.check_killstreaks(value):
                item.killstreaks = True

            elif self.check_paint(value, item):
                item.paint = self.get_paint(value)

            elif self.check_spell(value, item):
                if item.spell:
                    item.spell += "," + self.get_spell(value)
                else:
                    item.spell = self.get_spell(value)

            elif self.check_effect(value, item):
                item.effect = self.get_spell(value)

            elif self.check_craftability(value):
                item.craftable = False
            
            elif self.check_parts(value):
                print(value)
                if item.parts:
                    item.parts += "," + self.get_part(value)
                else:
                    item.parts = self.get_part(value)
            
    #checkers
    def check_sheen_and_killstreaker(self, value):
        if "sheen" in value and "killstreaker" in value:
            return True
        return False
    
    def check_sheen(self, value):
        # Had to change from "Sheen" in value to value == "Sheen" because some fucker named Sheen had crafted an item and fucked me up
        if "sheen" in value and "properties" not in value:
            return True
        return False
    
    def check_killstreaker(self, value):
        if "killstreaker" in value:
            return True
        return False
    
    def check_killstreaks(self, value):
        if "killstreaks Active" in value:
            return True
        return False
    
    def check_paint(self, value, item):
        if "paint color" in value and item.type != "supply crate" and "style" not in value:
            return True
        return False
    
    def check_spell(self, value, item):
        if "spell" in value and item.name != "the point and shoot" and item.name != "spellbook magazine":
            return True
        return False

    def check_effect(self, value, item):
        if "unusual effect" in value and item.type != "supply crate":
            return True
        return False
    
    def check_craftability(self, value):
        if value == "( not usable in crafting )":
            return True
        return False
    
    def check_parts(self, value):
        if ":" in value and any(part in value for part in self.parts):
            return True
        return False
    

    # getters
    def get_sheen_and_killstreaker(self, value):
        """
        Args:
            value:
                str: "(killstreaker: incenerator, sheen: hot-rod)"

        returns:
            {"sheen" : str, "killstreaker" : str} 
            or None if not in correct format"""
        
        match = re.search(r"\(killstreaker: (?P<killstreaker>\D+), sheen: (?P<sheen>\D+)\)", value)
        if match:
            killstreaker = match.group("killstreaker")
            sheen = match.group("sheen")
            return {"sheen" : sheen, "killstreaker" : killstreaker}
    
    def get_sheen(self, value):
        match = re.search(r"sheen: (?P<sheen>[a-z0-9 .\-']+)", value)
        if match:
            return match.group("sheen")
   
    def get_paint(self, value):
        print(value)
        match = re.search(r"paint color: (?P<paint>[a-z0-9 .\-']+)", value)
        if match:
            return match.group("paint")
    
    def get_spell(self, value):
        print(value)
        match = re.search(r"halloween: (?P<spell>[a-z0-9 .\-']+)", value)
        if match:
            return match.group("spell")

    def get_effect(self, value):
        print(value)
        match = re.search(r"unusual effect: (?P<effect>[a-z0-9 .\-']+)", value)
        if match:
            return match.group("effect")
    
    def get_part(self, value):
        print(value)
        match = re.search(r"\((?P<part>[a-z0-9 .\-'ü]+):", value)
        if match:
            return match.group("part")
    

def main() -> None:
    """ blah"""
    shit = ["76561198383794129", "7379919002", "331369", "3108214489", "0", "1", "Killstreak Tide Turner", "Unique",
            "secondary", None, None, None, None, "1", None, None, None, None, None, None]

    item = Item(*shit)
    print(item)

if __name__ == "__main__":
    main()