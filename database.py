import sqlite3

from item import Item

class DB():
    def __init__(self, conn):
        self.connect = conn
        self.connect.row_factory = sqlite3.Row
        self.cursor = self.connect.cursor()
    
    def add_items(self, items: dict, column: str):
        for item in items:
            params = (item.steamid, item.assetid, item.classid, item.instanceid, item.tradable, item.craftable, item.name, item.quality, 
                    item.type, item.rarity, item.collection, item.exterior, item.sku, item.killstreaks, item.sheen,
                    item.killstreaker, item.paint, item.spell, item.effect, item.parts)

            self.cursor.execute(f'INSERT INTO {column} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', params)

    def compare_items(self, items: dict, column: str) -> list:
        new_items = []
        for item in items:
            if not self.check_if_item_exists(item, column):
                new_items.append(item)
        return new_items
    
    def get_steamids_from_categories(self, column: str, categories: list) -> list:
        steamids = []
        for category in categories:
            rows =  self.cursor.execute(f"SELECT steamid FROM {column} WHERE category = '{category}';").fetchall()
            steamids.extend([row[0] for row in rows])
        return steamids
    
    def get_all_steamids(self, column: str) -> list:
        rows = self.cursor.execute(f"SELECT steamid FROM {column};").fetchall()
        return [row[0] for row in rows]

    def check_if_item_exists(self, item: dict, column: str) -> dict:
        params = (item.steamid, item.assetid, item.classid, item.instanceid)
        result = self.cursor.execute(f"SELECT EXISTS (SELECT * FROM {column} WHERE steamid = (?) AND assetid = (?) AND classid = (?) AND instanceid = (?));", params)
        # fetches first object because of the row factory setting
        return bool(result.fetchone()[0])
    
    def delete_all_from_column(self, column: str) -> bool:
        self.cursor.execute(f"DELETE FROM {column}")
         
    def database_to_dict(self, column: str) -> dict:
        return [dict(row) for row in self.cursor.execute(f"SELECT * FROM {column};").fetchall()]
    
    def delete_from_column_where_steamid(self, column: str, steamid):
        if steamid:
            self.cursor.execute('DELETE FROM "{}" WHERE steamid = ?;'.format(column.replace('"', '""')), (steamid, ))

    # TESTING
    def test(self, column):
        result = self.cursor.execute(f"SELECT * FROM {column} WHERE spell == 'None';")
        result_result = result.fetchone()
        print(result_result)
        column = "new_stn_strange_bots"
        self.cursor.execute(f"INSERT INTO {column} ('steamid', 'assetid', 'classid', 'instanceid', 'tradable', 'craftable', 'name', 'quality', 'type', 'rarity', 'collection', 'exterior', 'sku', 'killstreaks', 'sheen', 'killstreaker', 'paint', 'spell', 'effect', 'parts') VALUES ({result_result});")