from database import DB

import json
import requests
import os
import time

class Schema():
    def __init__(self, filename: str = "items.db"):
        
        self.database = DB(filename)

    def get_schema_from_API(self, params, headers = {}) -> json:
        
        #API KEY: 
        #https://api.steampowered.com/IEconItems_<ID>/GetSchemaItems/v0001/?key=<API key>
        
        schema = {"items" : [], "time" : None}
        
        while True:
        
            response = requests.get(f"https://api.steampowered.com/IEconItems_440/GetSchemaItems/v0001/", params=params)

            if response.status_code != requests.codes.ok:
                return {"error" : response.status_code}
            
            print(response.status_code)

            try:
                result = response.json()["result"]
            except Exception as e:
                return {"Error" : e}

            schema['items'].extend(result['items'])
            
            if 'next' in result:
                params['start'] = result['next']
            else:
                break
        
        schema["time"] = time.ctime()
        return schema
    
    def save_schema_to_file(self, schema_json: json = None, filepath: str = "data/item_schema.json"):
        with open(filepath, "w") as file:
            json.dump(schema_json, file)

    def load_schema_from_file(self, filepath = "data/item_schema.json"):
        #self.database.execute()
        try:
            with open(filepath, "r") as file:
                schema = json.load(file)
                return schema
        except Exception:
            return False
        
    def get_schema(self, API_KEY: str = "", filepath: str = "data/item_schema.json") -> json:

        headers = {}
        params = {"key" : API_KEY,
                  "language" : "en"}
        

        schema = self.load_schema_from_file(filepath)
        if schema:
            headers = {"If-Modified-Since" : time.ctime(schema["time"])}
            response = requests.get('https://api.steampowered.com/IEconItems_440/GetSchemaOverview/v1/',
                    params=params, headers=headers)

            print(response.url)
            print(headers)
            print(response.status_code)
            
            if response.status_code == requests.codes.not_modified:
                return schema
            
            if not response.ok:
                return {"Error", "response status:" + response.status_code}

        params = {"key" : API_KEY,
                  "language" : "en"}

        schema = self.get_schema_from_API(params, headers)
        self.save_schema_to_file(schema_json=schema, filepath="data/item_schema.json")
        return schema