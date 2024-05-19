import requests
import pprint
import sqlite3
from time import time
import urllib.parse

API_KEY = "e92debb161c8d23c131e43184a47969c"

class Stn():
    def __init__(self, *, connect, table: str, api_key):
        self.conn = connect
        self.conn.row_factory = sqlite3.Row
        self.row_cursor = self.conn.cursor()
        self.default_table = table

        self.api_key = api_key

        self.PAGE_URL = "https://stntrading.eu"

# new STN beta API functions
# credit related functions
    def get_credits_from_api(self) -> int:
        url = "https://api.stntrading.eu/GetCredit/v1"
        r = requests.get(f"{url}?apikey={self.api_key}")
        r_json = r.json()
        return int(r_json["credit"])

    def get_credit_costs_from_api(self):
        url = "https://api.stntrading.eu/GetApiCosts/v1"
        r = requests.get(f"{url}?apikey={self.api_key}")
        r_json = r.json()
        return r_json["result"]

    def check_if_enough_credits(self, credits_needed: int) -> bool:
        my_credits = self.get_credits_from_api()
        return my_credits >= credits_needed

# schema and item details related functions
    def get_item_details_from_api(self, item_name: str) -> dict:
        url = "https://api.stntrading.eu/GetItemDetails/v1"
        r = requests.get(f"{url}?full_name={item_name}&apikey={self.api_key}")
        r_json = r.json()
        return r_json

    def add_item_details_to_database(self, item_details: dict):
        table = "stn_schema"
        name = item_details["full_name"]
        buy_keys = item_details["pricing"]["buy"]["keys"] 
        buy_metal = item_details["pricing"]["buy"]["metal"]
        sell_keys = item_details["pricing"]["sell"]["keys"]
        sell_metal = item_details["pricing"]["sell"]["metal"]
        current_stock = item_details["stock"]["level"]
        stock_limit = item_details["stock"]["limit"]
        insert_values = (buy_keys, buy_metal, sell_keys, sell_metal, current_stock, stock_limit, time(), name) # NAME HAS TO BE LAST
        self.row_cursor.execute(f"UPDATE {table} SET buy_keys = (?), buy_metal = (?), sell_keys = (?), sell_metal = (?), current_stock = (?), stock_limit = (?), time = (?) WHERE name = (?)", insert_values)
        self.conn.commit()

    def get_item_details_from_database(self, name):
        name = name.strip()
        return self.row_cursor.execute("SELECT * FROM stn_schema WHERE UPPER(name) = UPPER(?)", (name, )).fetchone()

    def get_item_schema_from_api(self, type: str = None) -> dict:
        url = "https://api.stntrading.eu/GetSchema/v1"
        if type:
            r = requests.get(f"{url}?apikey={self.api_key}&type={type}")
        else:
            r = requests.get(f"{url}?apikey={self.api_key}")
        r_json = r.json()
        return r_json

    def add_schema_to_database(self, schema: dict):
        table = "stn_schema"
        items = schema["result"]["schema"]
        for item in items:
            self.cursor.execute(f"INSERT OR IGNORE INTO {table} (name) VALUES (?)", (item, ))
        self.connect.commit()

# searches table
    def get_match_from_database(self, search):
        match = self.row_cursor.execute("SELECT match FROM searches WHERE UPPER(search) = UPPER(?)", (search, )).fetchone()
        if match:
            return match
        return None
    
    def add_match_to_database(self, search, match):
        self.row_cursor.execute("INSERT INTO searches VALUES (?, ?)", (search, match))

# link creator
    def create_item_link(self, item_name:str):
        formatted_query = urllib.parse.quote_plus(item_name)
        base_item_path = "https://stntrading.eu/item/tf2/"
        return f"{base_item_path}{formatted_query}"

# search func
    def search(self, search: str):
        # checks database for item
        item = self.get_item_details_from_database(search)
        if item:
            return item
        
        # checks previously searched table for match
            # if match checks if previous search has yielded any results
                # if has tries to return item
                # else returns None
        match = self.get_match_from_database(search)
        if match:
            if match["match"]:
                item = self.get_item_details_from_database(match["match"])
                if item:
                    return item
                print("could not find match from stn schema something went wrong")
                return None
            else:
                print("search has previously been tried and failed")
                return None
        
        print("hello world")
        # tries to get from API
        item = self.get_item_details_from_api(item_name=search)
        if item["success"]:
            # adds item to schema table
            self.add_item_details_to_database(item["item"])
            self.add_match_to_database(search=search, match=item["item"]["full_name"])
            self.conn.commit()
            
            item = self.get_item_details_from_database(item["item"]["full_name"])
            if item:
                return item
            print("couldn't find item from database with name that it just added it with what the fack man")
            return None
        # if not found finally adds search to table with no match
        self.add_match_to_database(search = search, match = None)
        self.conn.commit()
        


        # tries to find item from database
            #if fails checks if has previously been searched from searches
                # if succeeds gets item from database by using the match
                # if fails tries to get item from api
                    # if succeeds adds item to schema table and adds search and match to search table and returns item
                    # else adds search to search with other failed searches

def main() -> None:
    table = "stn_schema"

    conn = sqlite3.connect("data/items.db")
    stn = Stn(conn, "stn_schema") 

    print(stn.create_item_link("The Hair of the Dog"))

if __name__ == "__main__":
    main()