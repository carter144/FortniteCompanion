from flask import Flask, json, request
import requests
import os
from fortnite import Fortnite
import time


app = Flask(__name__)
fort = Fortnite("0a4b0694-1c21b6f7-b786539b-81c2aa52")

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
    
    request_body = {
        "recipient": {"id": sender_psid},
        "messaging_type": "RESPONSE",
        "message": {
            "text": "Choose an option:",
            "quick_replies":[
                {
                    "content_type":"text",
                    "title":"Item Shop",
                    "payload":"item_shop",
                    
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
    pass



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
        


def uploadFortniteImages(images):
    attachment_ids = []
    for image_url in images:
        json_data = {
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "is_reusable": True,
                        "url": image_url
                    }
                }
            }
        }
        r = requests.post("https://graph.facebook.com/v7.0/me/message_attachments?access_token=" + os.getenv("page_token"), json=json_data)
        json_results = json.loads(r.text)
        attachment_ids.append(json_results["attachment_id"])
    return attachment_ids





if __name__ == '__main__':
    app.run()