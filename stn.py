import requests
import json
import pprint
from bs4 import BeautifulSoup
import re
import sqlite3
import re

from data.config import config

class Stn():
    def __init__(self, connect, table: str):
        self.conn = connect
        self.conn.row_factory = sqlite3.Row
        self.row_cursor = self.conn.cursor()
        self.default_table = table

        self.PAGE_URL = "https://stntrading.eu"

        self.cookies = {
            'cf_clearance': 'LEtujJY1dM5iHdmk.8Aoj8yd_w.Ra4zC1xGafM2JCzM-1713639364-1.0.1.1-mGSv1oiS3WzPxuzOjR9FLJLiWw.WQgdzw_sIZE9w_NmJ3CreQhfHHPcgSrYR0IcYdhLp2hQ9Ti3Bs8B_621Pfg',
            'stn_hash': '0820147cb78d3beea0934ed540e48da3',
            '__cflb': '0H28vBBkjWkeFGpkqAzJEXRDzPd1g8MfvmSJwCRP44d',
            'browser': '1',
        }

    def _search(self, search: str) -> json:
        json_data = [
            {
                'indexName': 'products',
                'params': {
                    'facets': [
                        'categories.lvl0',
                        'in_stock',
                        'key_value',
                        'tf2.collection',
                        'tf2.grade',
                        'tf2.quality',
                        'tf2.unusual_effect',
                    ],
                    'highlightPostTag': '__/ais-highlight__',
                    'highlightPreTag': '__ais-highlight__',
                    'hitsPerPage': 40,
                    'maxValuesPerFacet': 250,
                    'page': 0,
                    'query': search,
                    'tagFilters': '',
                },
            },
        ]

        result = self.get_or_post_page("POST", "https://stntrading.eu/api/search", json_data)
        if result["success"]:
            return result["result"].json()
        return result
    
    # formatters
    def get_only_numbers(self, string: str) -> float:
        lol = re.search(r'(\d+\.?\d{0,2})', string)
        if lol:
            return lol.group()
        return 0

    def format_price(self, price: str) -> dict:
        new_price = price.lower()
        if "," in new_price:
            new_price = new_price.split(",")
        else:
            new_price = [new_price]

        prices = {"keys" : None, "metal" : None}
        for unit in new_price:
            if "key" in unit:
                prices["keys"] = self.get_only_numbers(unit)
            elif "ref" in unit:
                prices["metal"] = self.get_only_numbers(unit)   

        return prices
    
    def format_name(name: str) -> str:
        name = name.lower()
        if "unusual" in name and "taunt" not in name:
            name = name.replace("unusual", "")

        return name.strip()

    def format_search(self, search_json: json) -> dict:
        items_json = search_json["results"][0]["hits"]
        items = []
        for item_json in items_json:
            price = self.format_price(item_json["price_as_string"])
            item = {"id" : item_json["objectID"],
                    "sku" : None,
                    "name" : item_json["name"], 
                    "buy_keys" : price["keys"],
                    "buy_metal" : price["metal"],
                    "sell_keys" : None,
                    "sell_metal" : None,
                    "url" : self.PAGE_URL + item_json["page_url"]}
            items.append(item)
        return items
    

    def get_prices_from_link(self, link: str) -> dict:
        result = self.post_page(link)
        if result["success"]:
            #with open("data/deleteme.html", "w") as file:
            #    file.write(result["result"].text)
            soup = BeautifulSoup(result["result"].content, "html.parser")
            div_tags = soup.find_all("div", {"class": "col-sm-6"})
            prices = {}
            for div in div_tags:
                paragraphs = div.find_all("p")
                prices.update(self._get_prices_from_paragraphs(paragraphs))
            return prices
        return result
    
    def _get_prices_from_paragraphs(self, paragraphs):
        if "Sell" in paragraphs[0].text:
            return {"sell_price" : paragraphs[1].text, "can_sell" : re.sub("\D", "", paragraphs[2].text)}

        elif "Buy" in paragraphs[0].text:
            item = {"buy_price" : paragraphs[1].text}
            if "Stock" in paragraphs[2].text:
                item["can_buy"] = re.sub("\D", "", paragraphs[2].text)
            return item

    def get_or_post_page(self, get_or_post: str, link: str, json_data: json = None):
        """ Creates post request with correct headers and cookies 
        
        Args:
            get_or_post:
                string like "GET" or "POST"
            link:
                string like 'https://stntrading.eu/item/tf2/Shoestring+Santa'
            json_data:
                optional json for requests that require it

        returns:
            {"success" : 1, "result" : ...}
            {"success" : 0, "error" : ...} """

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'null',
            'Alt-Used': 'stntrading.eu',
            'Connection': 'keep-alive',
            # 'Cookie': 'cf_clearance=LEtujJY1dM5iHdmk.8Aoj8yd_w.Ra4zC1xGafM2JCzM-1713639364-1.0.1.1-mGSv1oiS3WzPxuzOjR9FLJLiWw.WQgdzw_sIZE9w_NmJ3CreQhfHHPcgSrYR0IcYdhLp2hQ9Ti3Bs8B_621Pfg; stn_hash=0820147cb78d3beea0934ed540e48da3; __cflb=0H28vBBkjWkeFGpkqAzJEXRDzPd1g8MfvmSJwCRP44d; browser=1',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
        }

        try:
            if "post" in get_or_post.lower():
                response = requests.post(link, headers = headers, json = json_data, cookies = self.cookies)
            elif "get" in get_or_post.lower():
                response = requests.get(link, headers = headers, json = json_data, cookies = self.cookies)
            else:
                print("get_or_post_page, variable get_or_post not specified in correct format, defaulting to get...")
                response = requests.get(link, headers = headers, json = json_data, cookies = self.cookies)

        except Exception as e:
            return {"success" : False, "error" : e}
        
        if "https://steamcommunity.com" in response.url:
            return {"success" : False, "error" : "redirect to steam login, most likely issue in cookies"}
        
        return {"success" : True, "result" : response}


    # sql
    def check_if_id_exists(self, table: str, id: str) -> int:
        results = self.row_cursor.execute(f"SELECT EXISTS (SELECT * FROM {table} WHERE id = ?);", (str(id), )).fetchone()[0]
        return results

    def add_item(self, table: str, item: dict):
        # will only add unique items because of primary key constraint on id
        if not self.check_if_id_exists(table, id):
            self.row_cursor.execute(f"INSERT OR IGNORE INTO {table} VALUES (?, ?, ?, ?, ?, ?, ?, ?);", list(item.values()))

        self.conn.commit()


    def search(self, search: str):
        # check if found in database
        # TODO: change (name) to some modifyable column variable
        if find := self.search_database(search):
            return find

        # if not found in database
        search_dict = self._search(search)
        formated_search = self.format_search(search_dict)

        for item in formated_search:
            self.add_item("stn_schema", item)

        self.conn.commit()

        if find := self.search_database(search):
            return find
        
    def search_database(self, search: str) -> set:
        """ Creates different search parameters and returns in any of them gets a match """

        # search with the default name
        if find := self.row_cursor.execute(f"SELECT * FROM {self.default_table} WHERE UPPER(name) LIKE UPPER(?)", (search, )).fetchone():
            return find
        
        # search with "The " appended to begining of item name 
        if find := self.row_cursor.execute(f"SELECT * FROM {self.default_table} WHERE UPPER(name) = UPPER(?)", (f"The {search}", )).fetchone():
            return find

def main() -> None:
    db = config["database_file_path"]
    table = "stn_schema"

    conn = sqlite3.connect(db)
    stn = Stn(conn, "stn_schema") 

    print(stn.search("firebrand")["url"])

if __name__ == "__main__":
    main()