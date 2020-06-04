from flask import Flask, json, request
import requests
import os


app = Flask(__name__)

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
    response = ""

    if received_message["text"]:
        response = {"text": "carterisawesome"}
    callSendAPI(sender_psid, response)
    pass



def handlePostback(sender_psid, received_postback):
    pass

def callSendAPI(sender_psid, response):
    request_body = {
        "recipient": {"id": sender_psid},
        "message": response
    }


    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + os.getenv("page_token"), data=request_body)






if __name__ == '__main__':
    app.run()