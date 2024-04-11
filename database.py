import sqlite3

from item import Item

class DB():
    def __init__(self, filename: str):
        self.connect = sqlite3.connect(filename)
        self.cursor = self.connect.cursor()
    
    def add_items(self, items: dict, column: str):
        for item in items:
            params = (item["steamid"], item["assetid"], item['classid'], item['instanceid'], item['tradable'], item["craftable"], item['name'], item['quality'], 
                    item['type'], item['rarity'], item['collection'], item['exterior'], item['sku'], item["killstreaks"], item["sheen"],
                    item["killstreaker"], item["paint"], item["spell"], item["effect"], item["parts"])

            self.cursor.execute(f'INSERT INTO {column} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', params)
        self.connect.commit()

    def compare_items(self, items: dict, column: str) -> list:
        new_items = []
        for item in items:
            if not self.check_if_item_exists(item, column):
                new_items.append(item)
        return new_items
    
    def get_steamids_by_category(self, column: str, category: str) -> list:
        rows =  self.cursor.execute(f"SELECT steamid FROM {column} WHERE category = '{category}';").fetchall()
        return [row[0] for row in rows]
    
    def get_all_steamids(self, column: str) -> list:
        rows = self.cursor.execute(f"SELECT steamid FROM {column};").fetchall()
        return [row[0] for row in rows]


    def check_if_item_exists(self, item: dict, column: str) -> dict:
        params = (item["assetid"], item['classid'], item['instanceid'])
        result = self.cursor.execute(f"SELECT * FROM {column} WHERE assetid = (?) AND classid = (?) AND instanceid = (?);", params)
        return bool(result.fetchone())
    
    def delete_all_from_column(self, column: str) -> bool:
        try:
            self.cursor.execute(f"DELETE FROM {column}")
            return True
        except Exception:
            return False
    
    def find_valuable_items_database(self, column: str) -> dict:
        valuable_items = []
        
        # paint
        white = self.cursor.execute(f"SELECT * FROM {column} WHERE paint = 'An Extraordinary Abundance of Tinge';").fetchall()
        black = self.cursor.execute(f"SELECT * FROM {column} WHERE paint = 'A Distinctive Lack of Hue';").fetchall()
        lime = self.cursor.execute(f"SELECT * FROM {column} WHERE paint = 'The Bitter Taste of Defeat and Lime';").fetchall()
        pink = self.cursor.execute(f"SELECT * FROM {column} WHERE paint = 'A Distinctive Lack of Hue';").fetchall()
        # checks if fire horns or tornado with good sheens
        killstreaker = self.cursor.execute(f"SELECT * FROM {column} WHERE (killstreaker = 'Fire Horns' OR killstreaker = 'Tornado') AND (sheen = 'Team Shine' OR sheen = 'Villainous Violet' OR sheen = 'Hot Rod');").fetchall()
        # checks for spelled items
        spells = self.cursor.execute(f"SELECT * FROM {column} WHERE spell != 'None';").fetchall()
        # checks for strange parts
        parts = self.cursor.execute(f"SELECT * FROM {column} WHERE (parts = 'Dominations' OR parts = 'Damage Dealt' OR parts = 'Player Hits');").fetchall()

        valuable_lists = [white, black, lime, pink, killstreaker, spells, parts]

        for valuable_list in valuable_lists:
            if valuable_list != None:
                valuable_items.extend(valuable_list)

        valuable_list = list(set(valuable_list))

        valuable_items_objects = []
        for row in valuable_items:
            valuable_items_objects.append(Item.from_params_to_dict(*row))

        return valuable_items_objects

    def test(self, column):
        result = self.cursor.execute(f"SELECT * FROM {column} WHERE spell == 'None';")
        result_result = result.fetchone()
        print(result_result)
        column = "new_stn_strange_bots"
        self.cursor.execute(f"INSERT INTO {column} ('steamid', 'assetid', 'classid', 'instanceid', 'tradable', 'craftable', 'name', 'quality', 'type', 'rarity', 'collection', 'exterior', 'sku', 'killstreaks', 'sheen', 'killstreaker', 'paint', 'spell', 'effect', 'parts') VALUES ({result_result});")