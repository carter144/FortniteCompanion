from flask import Flask, json, request
import requests
import os
from fortnite import Fortnite
from ContinuedConversations import ContinuedConversations
import time
from QuickReplies import QuickReplies
from usernames import Usernames

app = Flask(__name__)
fort = Fortnite("0a4b0694-1c21b6f7-b786539b-81c2aa52")
conversations = ContinuedConversations()
usernames = Usernames()

@app.route('/webhook', methods=['GET'])
def get_webhook():

    VERIFY_TOKEN = "cartervan"
    mode = request.args.get("hub.mode", "")

    token = request.args.get("hub.verify_token", "")

    challenge = request.args.get("hub.challenge", "")

    json_obj = [{
        "mode": mode,
        "token": token,
        "challenge": challenge
    }]

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge
        else:
            return json.dumps({'success':False}), 403, {'ContentType':'application/json'} 

@app.route('/webhook', methods=['POST'])
def post_webhook():
    data = request.get_json()
    json_object = data["object"]
    if json_object == "page":
        entries = data["entry"]
        for entry in entries:
            webhook_event = entry["messaging"][0]
            sender_psid = webhook_event["sender"]["id"]
            
            if webhook_event["message"]:
                handleMessage(sender_psid, webhook_event["message"])
            elif webhook_event["postback"]:
                handlePostback(sender_psid, webhook_event["postback"])
        return "EVENT_RECEIVED"

    else:
        return json.dumps({'success':False}), 403, {'ContentType':'application/json'}

    return json.dumps(data)
  

def handleMessage(sender_psid, received_message):
    #getItemShop(sender_psid)
    print("received_message: ", received_message)
    print("self.user_ids: ", conversations.getUserIds())
    print("usernames: ", usernames.getUsernames())
    post_toggle_sender_action(sender_psid, True)
    if conversations.hasUserQuickReplied(sender_psid):
        reply_to_what = conversations.getConversationFrom(sender_psid)
        if reply_to_what == QuickReplies.STATS.value:
            # Expect to receive a username from user
            username = received_message["text"]
            conversations.removeUserId(sender_psid)
            usernames.addUserIdAndUsername(sender_psid, username)
            post_quick_replies_stat_menu(sender_psid)
        else:
            print("How did I get to the reply part?")
    elif "quick_reply" in received_message:
        payload = received_message["quick_reply"]["payload"]
        if payload == QuickReplies.SHOP.value:
            getItemShop(sender_psid)
            post_quick_replies_menu(sender_psid)
        elif payload == QuickReplies.STATS.value:
            conversations.addUserIdAndConversation(sender_psid, QuickReplies.STATS.value)
            print(conversations.getUserIds())
            post_text_message(sender_psid, "Stats for which account name?")
        elif payload == QuickReplies.MAP.value:
            handle_map_request(sender_psid)
            post_quick_replies_menu(sender_psid)
        elif payload == QuickReplies.VISIT.value:
            handle_visit_request(sender_psid)
            post_quick_replies_menu(sender_psid)
        elif payload == QuickReplies.SOLO.value:
            handle_stats_request(sender_psid, QuickReplies.SOLO.value)
        elif payload == QuickReplies.DUO.value:
            handle_stats_request(sender_psid, QuickReplies.DUO.value)
        elif payload == QuickReplies.SQUAD.value:
            handle_stats_request(sender_psid, QuickReplies.SQUAD.value)
        elif payload == QuickReplies.ALL.value:
            handle_stats_request(sender_psid, QuickReplies.ALL.value)
    else:
        post_quick_replies_menu(sender_psid)
    post_toggle_sender_action(sender_psid, False)

def handlePostback(sender_psid, received_postback):
    print(received_postback)
    pass

def callSendAPI(sender_psid, response):
    request_body = {
        "recipient": {"id": sender_psid},
        "message": response
    }
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)

def getItemShop(sender_psid):
    shop_items = fort.getShopData()
    request_body = {"batch": []}

    for item in shop_items:
        message_details = {}
        if item.attachment_id:
            if item.item_type == "emote":
                message_details = {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "media",
                            "elements": [
                                {
                                    "media_type": "image",
                                    "attachment_id": item.attachment_id,
                                    "buttons": [
                                        {
                                            "type": "web_url",
                                            "url": fort.construct_fortnite_youtube_search_url(item),
                                            "title": "See Emote on YouTube",
                                        }
                                    ]
                                }
                            ]
                        }
                    }    
                }
        else:
            message_details = {
                "attachment":{
                    "type":"image", 
                    "payload":{
                        "url":item.background_image_url, 
                        "is_reusable": "true"
                    }
                }
            }

        json_obj = {
            "method": "POST",
            "relative_url":"me/messages",
            "body": "recipient={\"id\":\"" + sender_psid + "\"}&message=" + json.dumps(message_details)
        }

        request_body["batch"].append(json_obj)
        
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)
        

def handle_stats_request(sender_psid, stat_type):
    username = usernames.getUsernameFrom(sender_psid)
    if username is None:
        post_text_message(sender_psid, "Let's retry that!")
        conversations.removeUserId(sender_psid)
        post_quick_replies_menu(sender_psid)
        return
    post_player_stats(sender_psid, username, stat_type)
    usernames.removeUserId(sender_psid)
    post_quick_replies_menu(sender_psid)

def post_player_stats(sender_psid, username, stat_type):
    stats = []
    if stat_type == QuickReplies.ALL.value:
        stats = fort.getPlayerAllStats(username)
    else:
        stats = fort.getPlayerStats(username, stat_type)

    msg = ""
    for val in stats:
        if val[1] == "":
            msg += f'{val[0]}\n'
        elif val[0]:
            msg += f'{val[0]}: {val[1]}\n'
        else:
            msg += '\n'
    post_text_message(sender_psid, msg)

def post_quick_replies_menu(sender_psid):
    request_body = {
        "recipient": {"id": sender_psid},
        "messaging_type": "RESPONSE",
        "message": {
            "text": "What do you want to see?",
            "quick_replies":[
                {
                    "content_type":"text",
                    "title":"Item Shop",
                    "payload":"item_shop"
                },
                {
                    "content_type":"text",
                    "title":"Stats",
                    "payload":"stats",
                    
                },
                {
                    "content_type":"text",
                    "title":"Map",
                    "payload":QuickReplies.MAP.value,
                },
                {
                    "content_type":"text",
                    "title":"Visit",
                    "payload": QuickReplies.VISIT.value
                }
            ]
        }
    }

    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)
    

def post_quick_replies_stat_menu(sender_psid):
    request_body = {
        "recipient": {"id": sender_psid},
        "messaging_type": "RESPONSE",
        "message": {
            "text": "Which stats?",
            "quick_replies":[
                {
                    "content_type":"text",
                    "title":"All",
                    "payload":QuickReplies.ALL.value
                },
                {
                    "content_type":"text",
                    "title":"Solo",
                    "payload":QuickReplies.SOLO.value
                },
                {
                    "content_type":"text",
                    "title":"Duo",
                    "payload":QuickReplies.DUO.value,
                },
                                    {
                    "content_type":"text",
                    "title":"Squad",
                    "payload":QuickReplies.SQUAD.value,
                },
            ]
        }
    }
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)

def post_text_message(sender_psid, message):
    request_body = {
      "recipient": {
        "id": sender_psid
      },
      "message": {
        "text": message
      }
    }
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)

# Typing indicator on Facebook messenger
def post_toggle_sender_action(sender_psid, is_typing_on):
    request_body = {
        "recipient": {
            "id": sender_psid
        },
        "sender_action": "typing_on" if is_typing_on else "typing_off"
    }
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)

def handle_map_request(sender_psid):
    map_url = fort.get_map_url()
    request_body = {
      "recipient": {
        "id": sender_psid
      },
        "message":{
            "attachment":{
                "type":"image", 
                "payload":{
                    "url":map_url, 
                    "is_reusable":"true"
                }
            }
        }
    }
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)

def handle_visit_request(sender_psid):
    request_body = {
        "recipient":{
        "id":sender_psid
        },
        "message":{
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"generic",
                    "elements": [
                        {
                            "title": "Epic Games Pages",
                            "image_url": "https://scontent-iad3-1.xx.fbcdn.net/v/t1.0-9/91851488_3244434952300473_5794185880470028288_o.jpg?_nc_cat=1&_nc_sid=6e5ad9&_nc_ohc=5XGV1tip8FMAX-bZMQJ&_nc_ht=scontent-iad3-1.xx&oh=60a041c0fda33d76af32975b35355022&oe=5F071E08",
                            "subtitle":"View extra content",
                            "buttons":[
                                {
                                    "type":"web_url",
                                    "url":"https://www.epicgames.com",
                                    "title":"Epic Games Website",
                                    "webview_height_ratio": "full"
                                },
                                {
                                    "type":"web_url",
                                    "url":"https://www.facebook.com/FortniteGame/",
                                    "title":"Fortnite Facebook",
                                    "webview_height_ratio": "full"
                                },
                                {
                                    "type":"web_url",
                                    "url":"https://www.facebook.com/epicgames/",
                                    "title":"Epic Games Facebook",
                                    "webview_height_ratio": "full"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)

if __name__ == '__main__':
    app.run()