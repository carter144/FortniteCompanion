class ContinuedConversations: 
    def __init__(self):
        self.user_ids = dict()

    def addUserIdAndConversation(self, sender_psid, conversation):
        self.user_ids[sender_psid] = conversation

    def removeUserId(self, sender_psid):
        if sender_psid in self.user_ids:
            self.user_ids.pop(sender_psid)
    
    def getConversationFrom(self, sender_psid):
        return self.user_ids[sender_psid]

    def hasUserQuickReplied(self, sender_psid):
        return True if sender_psid in self.user_ids else False

    def getUserIds(self):
        return self.user_ids

