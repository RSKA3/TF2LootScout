import requests
import json
import pprint
from bs4 import BeautifulSoup
import re

class Stn():
    def __init__(self):
        self.PAGE_URL = "https://stntrading.eu"

        self.cookies = {"browser":"1", 
                   "cf_clearance":"PN4xWV29tqhZe3U5wXHBLoViL6OQQshiJAJDmxE7_Lw-1712923842-1.0.1.1-nuXe8cBvs59iyv40vJ9UT7_gGEYZlLvq4czdCKs7nvanZH8FU3pFiypocU.JDD6pVKZ9958f9qsSeE_e3vE_2w", 
                   "stn_hash":"0820147cb78d3beea0934ed540e48da3", 
                   "browser":"1", "__cflb":"0H28vBBkjWkeFGpkqAzJEXRDzPd1g8MfwJSwq8v9Bjs"}

    def search(self, search: str) -> json:
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

        result = self.get_page("https://stntrading.eu/api/search", json_data)
        if result["success"]:
            return result["result"].json()
        return result
    
    def get_objects_from_search(self, search_json: json) -> dict:
        items_json = search_json["results"][0]["hits"]
        items = []
        for item_json in items_json:
            item = {"id" : item_json["objectID"], 
                    "name" : item_json["name"], 
                    "buy_price" : item_json["price_as_string"],
                    "sell_price" : None, 
                    "url" : self.PAGE_URL + item_json["page_url"]}
            items.append(item)
        return items
    
    def get_prices_from_link(self, link: str) -> dict:
        result = self.get_page(link)
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


    
    def get_page(self, link, json_data: json = None):
        headers = {
            #'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1_0; like Mac OS X) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/51.0.1335.157 Mobile Safari/535.2'
            "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"
        }

        try: 
            response = requests.get(link, headers = headers, json = json_data, cookies = self.cookies)
        except Exception as e:
            return {"success" : False, "error" : e}
        
        if "https://steamcommunity.com" in response.url:
            return {"success" : False, "error" : "redirect to steam login, most likely issue in cookies"}
        
        return {"success" : True, "result" : response}
    
stn = Stn()
print(stn.get_prices_from_link("https://stntrading.eu/item/tf2/Antarctic+Eyewear"))