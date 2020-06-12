import requests
import json
import os
from util import Utils
from QuickReplies import QuickReplies
from ShopItem import ShopItem

class Fortnite:

    def __init__(self, api_key):
        self.api_key = api_key
        # Name of shop item with attachment ID from Facebook
        self.attachments = dict()

    def getShopData(self):
        r = requests.get("https://fortniteapi.io/shop?lang=en", headers={"Authorization": self.api_key})
        print("Attachment IDs")
        print(self.attachments)
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
                image_url = item["full_background"]
                name = item["name"]
                item_type = item["type"]

                # Only do emotes for the time being because this process takes awhile. Need attachment IDs for templates
                # if item_type == "emote" and not name in self.attachments:
                #     response = self.attachment_upload(image_url)
                #     self.attachments[name] = response["attachment_id"]
                
                item = ShopItem(name, item_type, image_url, self.attachments.get(name, None))
                res.append(item)
        return res

    def getShopEmotes(self):
        r = requests.get("https://fortniteapi.io/shop?lang=en", headers={"Authorization": self.api_key})
        print("Attachment IDs")
        print(self.attachments)
        return self.parseShopEmotes(r.text)

    def parseShopEmotes(self, raw_data):
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
                item_type = item["type"]
                if item_type != "emote":
                    continue
                image_url = item["full_background"]
                name = item["name"]

                if not name in self.attachments:
                    response = self.attachment_upload(image_url)
                    self.attachments[name] = response["attachment_id"]
                
                item = ShopItem(name, item_type, image_url, self.attachments.get(name, None))
                res.append(item)
        return res

    def getPlayerAllStats(self, name):
        r_username = requests.get(f'https://fortniteapi.io/lookup?username={name}', headers={"Authorization": self.api_key})
        account_json_data = r_username.json()
        if "account_id" in account_json_data:
            account_id = account_json_data["account_id"]
        else:
            stats = []
            stats.append((f'{name} does not exist in Fortnite', ''))
            return stats
        
        r_account_id = requests.get(f'https://fortniteapi.io/stats?account={account_id}', headers={"Authorization": self.api_key})
        
        stats_json_data = r_account_id.json()
        global_stats_json = stats_json_data["global_stats"]

        stats = []
        stats.append(("Name", stats_json_data["name"]))
        stats.append(("Level", stats_json_data["account"]["level"]))
        stats.append(("",""))
        
        lookup_values = [QuickReplies.SOLO.value, QuickReplies.DUO.value, QuickReplies.SQUAD.value]
        
        for val in lookup_values:
            if val not in global_stats_json:
                stats.append((f'No {str(val).capitalize()} stats available', ""))
                if val != lookup_values[-1]:
                    stats.append(("",""))
                continue
            retrieved_stats_json = global_stats_json[val]
            stats.append(("Type", str(val).capitalize()))
            stats.append(("K/D", retrieved_stats_json.get("kd", "0")))
            stats.append(("Number of kills", retrieved_stats_json.get("kills", "0")))
            stats.append(("Times placed Top 1", retrieved_stats_json.get("placetop1", "0")))
            stats.append(("Number of matched played", retrieved_stats_json.get("matchesplayed", "0")))

            time_played_in_mins = retrieved_stats_json.get("minutesplayed", "0")
            stats.append(("Total time played", Utils.display_time(int(time_played_in_mins) * 60)))
            if val != lookup_values[-1]:
                stats.append(("",""))
        return stats

    def getPlayerStats(self, name, stat_type):
        r_username = requests.get(f'https://fortniteapi.io/lookup?username={name}', headers={"Authorization": self.api_key})
        account_json_data = r_username.json()
        if "account_id" in account_json_data:
            account_id = account_json_data["account_id"]
        else:
            stats = []
            stats.append((f'{name} does not exist in Fortnite', ''))
            return stats
        
        r_account_id = requests.get(f'https://fortniteapi.io/stats?account={account_id}', headers={"Authorization": self.api_key})
        
        stats_json_data = r_account_id.json()
        global_stats_json = stats_json_data["global_stats"]
        if stat_type not in global_stats_json:
            stats = []
            stats.append((f'No {str(stat_type).capitalize()} stats available for {name}', ""))
            return stats

        retrieved_stats_json = global_stats_json[stat_type]

        # Parse out specific stats from json obj
        stats = []
        stats.append(("Name", stats_json_data["name"]))
        stats.append(("Level", stats_json_data["account"]["level"]))
        stats.append(("",""))
        stats.append(("Type", str(stat_type).capitalize()))
        stats.append(("K/D", retrieved_stats_json.get("kd", "0")))
        stats.append(("Number of kills", retrieved_stats_json.get("kills", "0")))
        stats.append(("Times placed Top 1", retrieved_stats_json.get("placetop1", "0")))
        stats.append(("Number of matched played", retrieved_stats_json.get("matchesplayed", "0")))

        time_played_in_mins = retrieved_stats_json.get("minutesplayed", "0")
        stats.append(("Total time played", Utils.display_time(int(time_played_in_mins) * 60)))
        return stats

    def construct_fortnite_youtube_search_url(self, item):
        name = item.name
        item_type = item.item_type
        
        search_phrase = (name + ' ' + item_type).replace(" ", "+")

        search_url = f'https://www.youtube.com/results?search_query=fortnite+{search_phrase}'
        return search_url

    def attachment_upload(self, url):
        request_body = {
            "message":{
                "attachment":{
                    "type":"image", 
                    "payload":{
                        "is_reusable": "true",
                        "url": url
                    }
                }
            }
        }

        response = requests.post("https://graph.facebook.com/v7.0/me/message_attachments?access_token=" + os.getenv("page_token"), json=request_body)
        return response.json()

    def get_map_url(self):
        return "https://media.fortniteapi.io/images/map.png?showPOI=true"

