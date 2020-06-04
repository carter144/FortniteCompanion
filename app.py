from flask import Flask, json, request

companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

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
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
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
    		print(webhook_event)
    	return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    else:
    	return json.dumps({'success':False}), 403, {'ContentType':'application/json'}

    return json.dumps(data)
  

if __name__ == '__main__':
    app.run()