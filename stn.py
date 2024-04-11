import requests
import json
import pprint

PAGE_URL = "https://stntrading.eu"

class Stn():
    def search(self, search: str) -> json:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1_0; like Mac OS X) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/51.0.1335.157 Mobile Safari/535.2'
        }

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


        response = requests.post(f"https://stntrading.eu/api/search", headers = headers, json = json_data)
        return response.json()
    
    def get_objects_from_search(self, search_json: json) -> dict:
        items_json = search_json["results"][0]["hits"]
        items = []
        for item_json in items_json:
            item = {"id" : item_json["objectID"], "name" : item_json["name"], "price" : item_json["price_as_string"], "url" : PAGE_URL + item_json["page_url"]}
            items.append(item)
        return items
    

    
stn = Stn()
search_json = stn.search("The Cool Warm Sweater")
items = stn.get_objects_from_search(search_json)
print(items)
