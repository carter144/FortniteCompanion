class Usernames: 
    def __init__(self):
        self.user_ids = dict()

    def addUserIdAndUsername(self, sender_psid, username):
        self.user_ids[sender_psid] = username

    def removeUserId(self, sender_psid):
        self.user_ids.pop(sender_psid)
    
    def getUsernameFrom(self, sender_psid):
        return self.user_ids.get(sender_psid)
