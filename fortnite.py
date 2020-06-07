import requests
import json
from util import Utils

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

    def getPlayerStats(self, name, type):
        r_username = requests.get(f'https://fortniteapi.io/lookup?username={name}', headers={"Authorization": self.api_key})
        account_json_data = r_username.json()
        account_id = account_json_data["account_id"]
        
        r_account_id = requests.get(f'https://fortniteapi.io/stats?account={account_id}', headers={"Authorization": self.api_key})
        stats_json_data = r_account_id.json()

        global_stats_json = stats_json_data["global_stats"]
        retrieved_stats_json = global_stats_json[type]

        # Parse out specific stats from json obj
        stats = dict()
        stats["Name"] = stats_json_data["name"]
        stats["Level"] = stats_json_data["account"]["level"]
        stats["K/D"] = retrieved_stats_json["kd"]
        stats["Number of kills"] = retrieved_stats_json["kills"]
        stats["Times placed Top 1"] = retrieved_stats_json["placetop1"]
        stats["Number of matched played"] = retrieved_stats_json["matchesplayed"]

        time_played_in_mins = retrieved_stats_json["minutesplayed"]
        stats["Total time played"] = Utils.display_time(int(time_played_in_mins) * 60)
        return stats

