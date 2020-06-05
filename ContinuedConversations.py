class ContinuedConversations: 
    user_ids = set()

    def __init__(self):
        pass

    def addId(self, sender_psid):
        self.user_ids.add(sender_psid)

    def removeId(self, sender_psid):
        self.user_ids.remove(sender_psid)
        