import requests
import json
class Fortnite:

    def __init__(self, api_key):
        self.api_key = api_key


    def getShopData(self):
        r = requests.get("https://fortniteapi.io/shop?lang=en", headers={"Authorization": self.api_key})


        return self.parseShopItems(r.text)

    def parseShopItems(self, raw_data):
        json_data = json.loads(raw_data)
        res = []
        # json_data.keys(): daily, featured, special, etc
        for key in json_data.keys():
            current_list_of_items = json_data[key]
            if type(current_list_of_items) is not list:
                continue
            #current_list_of_items is the list of items under featured or list of items under daily etc.
            for item in current_list_of_items:
                # each item is something in the itemshop
                res.append(item["full_background"])
        return res


    def getPlayerStats(self, name):
        r_username = requests.get(f'https://fortniteapi.io/lookup?username={name}', headers={"Authorization": self.api_key})
        account_json_data = r_username.json()
        account_id = account_json_data["account_id"]
        
        r_account_id = requests.get(f'https://fortniteapi.io/stats?account={account_id}', headers={"Authorization": self.api_key})
        stats_json_data = r_account_id.json()
        
        stats = dict()
        stats["name"] = stats_json_data["name"]
        stats["level"] = stats_json_data["account"]["level"]
        return stats




