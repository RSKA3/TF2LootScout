class Item():
    def init_item(self):
        # create Item dict
        self.item = {
            "steamid" : None,
            "classid" : None,
            "instanceid" : None,
            "assetid" : None,
            "tradable" : True,
            "craftable" : True,
            "name" : None,
            "quality" : None,
            "type" : None,
            "rarity" : None,
            "collection" : None,
            "exterior" : None,
            "sku" : None,
            "killstreaks" : None,
            "sheen" : None,
            "killstreaker" : None,
            "paint" : None,
            "spell" : None,
            "effect" : None,
            "parts" : None
            # steamid, classid, instanceid, assetid, tradeable, craftable, name, quality, type, rarity, collection, exterior, sku, killstreaks, sheen, killstreaker, paint, spell, effect, parts
        }


    def to_item(self, asset, description, steamid = None) -> dict:
        self.init_item()

        # fill in self.item
        self.item["assetid"] = asset["assetid"]
        self.item["steamid"] = steamid
        self.item["classid"] = description["classid"]
        self.item["instanceid"] = description["instanceid"]
        self.item["tradable"] = bool(description["tradable"])
        self.item["name"] = description["market_name"]

        # gets all tag values
        for tag in description["tags"]:
            self.item[self.get_tag(tag)] = tag["internal_name"]

        # gets all description values
        if "descriptions" in description:
            for description in description["descriptions"]:
                value = description["value"]
                self.get_description(description, self.item)

        return self.item
    
    def from_params_to_dict(self, steamid, classid, instanceid, assetid, tradeable, craftable, name, quality, type_, rarity, collection, exterior, sku, killstreaks, sheen, killstreaker, paint, spell, effect, parts = None):
        item = {
            "steamid" : steamid,
            "classid" : classid,
            "instanceid" : instanceid,
            "assetid" : assetid,
            "tradable" : tradeable,
            "craftable" : craftable,
            "name" : name,
            "quality" : quality,
            "type" : type_,
            "rarity" : rarity,
            "collection" : collection,
            "exterior" : exterior,
            "sku" : sku,
            "killstreaks" : killstreaks,
            "sheen" : sheen,
            "killstreaker" : killstreaker,
            "paint" : paint,
            "spell" : spell,
            "effect" : effect,
            "parts" : parts
            # steamid, classid, instanceid, assetid, tradeable, craftable, name, quality, type, rarity, collection, exterior, sku, killstreaks, sheen, killstreaker, paint, spell, effect, parts
        }

        return item

    
    def get_tag(self, tag):
        match tag["category"]:
            case "Quality":
                return "quality"
            case "Type":
                return "type"
            case "Rarity":
                return "rarity"
            case "Collection":
                return "collection"
            case "Exterior":
                return "exterior"
            
    def get_description(self, description, item):
        value = description["value"]

        if self.check_sheen_and_killstreaker(value, item):
            item["sheen"], self.item["killstreaker"] = self.get_sheen_and_killstreaker(value)
            item["killstreaks"] = True

        elif self.check_sheen(value, item):
            item["sheen"] = self.get_sheen(value)
            item["killstreaks"] = True

        elif self.check_killstreaker(value, item):
            item["killstreaks"] = True

        elif self.check_killstreaks(value, item):
            item["killstreaks"] = True

        elif self.check_paint(value, item):
            item["paint"] = self.get_paint(value)

        elif self.check_spell(value, item):
            if item["spell"]:
                item["spell"] += "," + self.get_spell(value)
            else:
                item["spell"] = self.get_spell(value)

        elif self.check_effect(value, item):
            item["effect"] = self.get_spell(value)

        elif self.check_craftability(value, item):
            item["craftable"] = False
        
        elif self.check_parts(value, item):
            if item["parts"]:
                item["parts"] += "," + self.get_part(value)
            else:
                item["parts"] = self.get_part(value)
            
    #checkers
    def check_sheen_and_killstreaker(self, value, item):
        if "Sheen" in value and "Killstreaker" in value:
            return True
        return False
    
    def check_sheen(self, value, item):
        if "Sheen" in value:
            return True
        return False
    
    def check_killstreaker(self, value, item):
        if "Killstreaker" in value:
            return True
        return False
    
    def check_killstreaks(self, value, item):
        if "Killstreaks Active" in value:
            return True
        return False
    
    def check_paint(self, value, item):
        if "Paint" in value and item["type"] != "Supply Crate" and "style" not in value:
            return True
        return False
    
    def check_spell(self, value, item):
        if "spell" in value and item["name"] != "The Point and Shoot" and item["name"] != "Spellbook Magazine":
            return True
        return False

    def check_effect(self, value, item):
        if "Unusual Effect" in value and self.item["type"] != "Supply Crate":
            return True
        return False
    
    def check_craftability(self, value, item):
        if value == "( Not Usable in Crafting )":
            return True
        return False
    
    def check_parts(self, value, item):
        # TODO: extend parts and make if statement more efficient
        parts = ["Airborne Enemies Killed", "Heavies Killed", "Demomen Killed", "Revenge Kills", "Domination Kills", "Soldiers Killed", "Full Moon Kills", 
                 "Cloaked Spies Killed", "Scouts Killed", "Engineers Killed", "Robots Destroyed", "Low-Health Kills", "Halloween Kills", "Robots Destroyed During Halloween"
                 "Underwater Kills", "Snipers Killed", "Kills While Übercharged", "Pyros Killed", "Defender Kills", "Medics Killed", "Tanks Destroyed"
                 "Medics Killed That Have Full ÜberCharge", "Giant Robots Destroyed", "Kills During Victory Time", "Robot Spies Destroyed", "Unusual-Wearing Player Kills"
                 "Spies Killed", "Burning Enemy Kills", "Killstreaks Ended", "Damage Dealt", "Point-Blank Kills", "Full Health Kills", "Robot Scouts Destroyed"
                 "Taunting Player Kills", "Not Crit nor MiniCrit Kills", "Player Hits", "Gib Kills", "Buildings Destroyed", "Headshot Kills", "Projectiles Reflected"
                 "Allies Extinguished", "Posthumous Kills", "Critical Kills", "Kills While Explosive Jumping", "Sappers Destroyed", "Long-Distance Kills"
                 "Kills with a Taunt Attack", "Freezecam Taunt Appearances", "Fires Survived", "Kills", "Assists", "Allied Healing Done"]
        if ":" in value and any(part in value for part in parts):
            return True
        return False


    # getters
    def get_sheen_and_killstreaker(self, value):
        killstreaker, sheen = value.split(",")
        killstreaker = killstreaker.replace("(Killstreaker: ", "")
        sheen = sheen.replace(" Sheen: ", "").replace(")", "")

        return [sheen, killstreaker]
    
    def get_sheen(self, value):
        return value.split("Sheen: ")[1]
    
    def get_killstreaker(self, value):
        return value.replace("Killstreaker: ", "")
    
    def get_paint(self, value):
        return value.replace("Paint Color: ", "")
    
    def get_spell(self, value):
        return value.replace("Halloween: ", "").replace("(spell only active during event)", "")

    def get_effect(self, value):
        return value.replace("★ Unusual Effect: ", "")
    
    def get_part(self, value):
        return value.split(":")[0].replace("(", "")