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
    print(received_message)
    if conversations.hasUserQuickReplied(sender_psid):
        reply_to_what = conversations.getConversationFrom(sender_psid)
        if reply_to_what == QuickReplies.STATS.value:
            # Expect to receive a username from user
            username = received_message["text"]
            conversations.removeUserId(sender_psid)
            usernames.addUserIdAndUsername(sender_psid, username)
            postQuickRepliesStatMenu(sender_psid)
        else:
            print("How did I get to the reply part?")
    elif "quick_reply" in received_message:
        payload = received_message["quick_reply"]["payload"]
        if payload == QuickReplies.SHOP.value:
            getItemShop(sender_psid)
            postQuickRepliesMenu(sender_psid)
        elif payload == QuickReplies.STATS.value:
            conversations.addUserIdAndConversation(sender_psid, QuickReplies.STATS.value)
            print(conversations.getUserIds())
            postTextMessage(sender_psid, "Stats for which account name?")
        elif payload == QuickReplies.SOLO.value:
            handleStatsRequest(sender_psid, QuickReplies.SOLO.value)
        elif payload == QuickReplies.DUO.value:
            handleStatsRequest(sender_psid, QuickReplies.DUO.value)
        elif payload == QuickReplies.SQUAD.value:
            handleStatsRequest(sender_psid, QuickReplies.SQUAD.value)
    else:
        postQuickRepliesMenu(sender_psid)

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
    image_urls = fort.getShopData()
    request_body = {"batch": []}

    for url in image_urls:
        message_details = {
            "attachment": {
                "type": "image",
                "payload": {
                        "is_reusable": "true",
                        "url": url 
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
        

def handleStatsRequest(sender_psid, type):
    username = usernames.getUsernameFrom(sender_psid)
    if username is None:
        postTextMessage(sender_psid, "Let's retry that!")
        conversations.removeUserId(sender_psid)
        postQuickRepliesMenu(sender_psid)
        return
    postPlayerStats(sender_psid, username, type)
    usernames.removeUserId(sender_psid)
    postQuickRepliesMenu(sender_psid)

def postPlayerStats(sender_psid, username, type):
    stats = fort.getPlayerStats(username, type)
    postTextMessage(sender_psid, '\n'.join(['%s: %s' % (key, value) for (key, value) in stats.items()]))

def postQuickRepliesMenu(sender_psid):
    request_body = {
            "recipient": {"id": sender_psid},
            "messaging_type": "RESPONSE",
            "message": {
                "text": "Choose an option:",
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
                        
                    }
                ]
            }
        }

    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)
    

def postQuickRepliesStatMenu(sender_psid):
    request_body = {
        "recipient": {"id": sender_psid},
        "messaging_type": "RESPONSE",
        "message": {
            "text": "Which stats?",
            "quick_replies":[
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

def postTextMessage(sender_psid, message):
    request_body = {
      "recipient": {
        "id": sender_psid
      },
      "message": {
        "text": message
      }
    }
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), json=request_body)



if __name__ == '__main__':
    app.run()