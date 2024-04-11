import requests
import pprint
import json

def main():

    search = "Mann of the Seven Sees"
    id = "76561199257781891"

    response_json = send_request(search)
    ids = get_ids(response_json)

    try:
        print(ids[id])
    except KeyError:
        print("not found")
    

def send_request(search = ""):
    params = {"side" : "market", "orderBy" : "price", "orderDir" : "asc", "title" : search, "priceFrom" : "0", "priceTo" : "0", "treeFilters" : "", "gameId" : "tf2", "types" : "dmarket", "cursor" : "", "limit" : "100", "currency" : "USD", "platform" : "browser", "isLoggedIn" : "true"}
    url = "https://api.dmarket.com/exchange/v1/market/items?"
    #https://api.dmarket.com/exchange/v1/market/items?side=market&orderBy=personal&orderDir=desc&title=&priceFrom=0&priceTo=0&treeFilters=&gameId=tf2&types=dmarket&cursor=&limit=100&currency=USD&platform=browser&isLoggedIn=true

    response = requests.get(url, params=params)
    print("status code", response.status_code)
    return response.json()

def get_ids(response):
    ids = {}
    for i, item in enumerate(response["objects"]):
        ids[item["extra"]["groupId"]] = i + 1
    return ids

if __name__ == "__main__":
    main()
